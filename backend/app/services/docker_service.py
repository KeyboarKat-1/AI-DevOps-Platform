import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import docker
    from docker.errors import DockerException
except Exception:  # pragma: no cover - docker may not be installed in test env
    docker = None
    DockerException = Exception


def _format_uptime(seconds: float) -> str:
    if seconds is None or seconds < 0:
        return 'unknown'
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts:
        parts.append(f"{int(seconds)}s")
    return ' '.join(parts)

logger = logging.getLogger(__name__)

# Simple in-memory cache to avoid frequent docker API calls
_cache_ts: float = 0.0
_cache_ttl: float = 5.0  # seconds
_cache_data: Optional[List[Dict[str, Any]]] = None

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if docker is None:
        return None
    try:
        _client = docker.from_env()
        return _client
    except DockerException:
        logger.exception("Failed to initialize Docker client")
        _client = None
        return None


def _ping_docker(client) -> bool:
    try:
        return client.ping()
    except DockerException:
        logger.debug("Docker ping failed", exc_info=True)
        return False
    except Exception:
        logger.debug("Unexpected Docker ping failure", exc_info=True)
        return False


def _safe_get(d: dict, *keys, default=None):
    try:
        for k in keys:
            d = d.get(k, {})
        return d if d != {} else default
    except Exception:
        return default


def _compute_cpu_percent(stats: dict) -> Optional[float]:
    try:
        # Follow Docker's CPU calculation formula
        cpu_stats = stats.get('cpu_stats', {}) or {}
        precpu = stats.get('precpu_stats', {}) or {}

        total_usage = cpu_stats.get('cpu_usage', {}).get('total_usage')
        prev_total = precpu.get('cpu_usage', {}).get('total_usage')
        system_cpu = cpu_stats.get('system_cpu_usage')
        prev_system = precpu.get('system_cpu_usage')

        # percpu usage may be a list or dict depending on docker version
        percpu_usage = cpu_stats.get('cpu_usage', {}).get('percpu_usage') or []
        cpu_count = len(percpu_usage) if isinstance(percpu_usage, (list, tuple)) else (len(percpu_usage) if isinstance(percpu_usage, dict) else 0)

        # If any required field is missing, return 0.0 as a safe fallback
        if total_usage is None or prev_total is None or system_cpu is None or prev_system is None or cpu_count == 0:
            return 0.0

        cpu_delta = float(total_usage) - float(prev_total)
        system_delta = float(system_cpu) - float(prev_system)

        if system_delta <= 0.0 or cpu_delta <= 0.0:
            return 0.0

        percent = (cpu_delta / system_delta) * cpu_count * 100.0
        return round(percent, 2)
    except (KeyError, ZeroDivisionError, TypeError, ValueError):
        logger.debug('Safe CPU calc failed with known error', exc_info=True)
        return 0.0
    except Exception:
        logger.exception('Unexpected error computing CPU percent')
        return 0.0


def _compute_mem_percent(stats: dict) -> Optional[float]:
    try:
        mem_stats = stats.get('memory_stats', {}) or {}
        usage = mem_stats.get('usage')
        limit = mem_stats.get('limit')
        if usage is None or not limit:
            return 0.0
        percent = (float(usage) / float(limit)) * 100.0
        return round(percent, 2)
    except (KeyError, ZeroDivisionError, TypeError, ValueError):
        logger.debug('Safe memory calc failed with known error', exc_info=True)
        return 0.0
    except Exception:
        logger.exception('Unexpected error computing memory percent')
        return 0.0


def get_containers(ttl: float = _cache_ttl) -> List[Dict[str, Any]]:
    """Return a list of running containers with lightweight metrics.

    Raises RuntimeError("Docker engine unavailable") when client can't be created.
    """
    global _cache_ts, _cache_data
    now = time.time()
    if now - _cache_ts < ttl and _cache_data is not None:
        return _cache_data

    client = _get_client()
    if client is None:
        raise RuntimeError('Docker engine unavailable')

    if not _ping_docker(client):
        raise RuntimeError('Docker engine unavailable')

    # Debug/logging for visibility
    try:
        print("Docker connected successfully")
    except Exception:
        logger.debug("Printed Docker connected message failed", exc_info=True)

    results: List[Dict[str, Any]] = []
    try:
        containers = client.containers.list(all=False)
        for c in containers:
            entry: Dict[str, Any] = {
                'name': getattr(c, 'name', None) or (c.attrs.get('Name').lstrip('/') if c.attrs.get('Name') else None),
                'status': getattr(c, 'status', None) or c.attrs.get('State', {}).get('Status'),
                'image': ','.join(c.image.tags) if getattr(c, 'image', None) and c.image.tags else (getattr(c, 'image', None).short_id if getattr(c, 'image', None) else None),
                'id': getattr(c, 'id', None),
            }
            # Safe one-shot stats call — may raise or return partial data
            try:
                stats = c.stats(stream=False)
                cpu = _compute_cpu_percent(stats)
                mem = _compute_mem_percent(stats)
                entry.update({'cpu_usage': cpu, 'memory_usage': mem})
            except Exception:
                # Do not fail the whole request if stats are temporarily unavailable
                logger.debug('Failed to fetch stats for container %s', entry.get('name'), exc_info=True)
                entry.update({'cpu_usage': None, 'memory_usage': None})

            try:
                started_at = c.attrs.get('State', {}).get('StartedAt')
                if started_at:
                    start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    uptime_seconds = time.time() - start_time.timestamp()
                    entry['uptime'] = _format_uptime(uptime_seconds)
                else:
                    entry['uptime'] = 'unknown'
            except Exception:
                entry['uptime'] = 'unknown'

            results.append(entry)

        # Debug: number of running containers
        try:
            print(f"Found {len(containers)} running containers")
        except Exception:
            logger.debug("Printed container count failed", exc_info=True)

        _cache_ts = now
        _cache_data = results
        return results
    except DockerException as exc:
        logger.exception('Docker API error')
        raise RuntimeError('Docker engine unavailable') from exc
    except Exception:
        logger.exception('Unexpected error while listing containers')
        raise
