from fastapi import APIRouter, HTTPException

try:
    import docker
    from docker.errors import DockerException, NotFound
except Exception:
    docker = None
    DockerException = Exception
    NotFound = Exception

from app.services.docker_service import get_containers

router = APIRouter()


@router.get('/docker/containers')
def list_containers():
    try:
        return get_containers()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch docker containers: {exc}") from exc


@router.get('/docker/containers/{container_id}/stats')
def container_stats(container_id: str):
    try:
        containers = get_containers()
        for container in containers:
            if container.get('id') == container_id or container.get('name') == container_id:
                return container
        raise HTTPException(status_code=404, detail='Container not found')
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch container stats: {exc}") from exc


def _get_client_or_400():
    if docker is None:
        raise HTTPException(status_code=503, detail='Docker SDK not available on server')
    try:
        client = docker.from_env()
        try:
            client.ping()
        except Exception:
            raise HTTPException(status_code=503, detail='Docker engine unavailable')
        return client
    except DockerException:
        raise HTTPException(status_code=503, detail='Docker engine unavailable')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/docker/{container_id}/stop')
def stop_container(container_id: str):
    client = _get_client_or_400()
    try:
        container = client.containers.get(container_id)
    except NotFound:
        raise HTTPException(status_code=404, detail='Container not found')
    except DockerException:
        raise HTTPException(status_code=503, detail='Docker engine unavailable')
    try:
        container.stop()
        return {"success": True, "message": "Container stopped successfully"}
    except DockerException as exc:
        raise HTTPException(status_code=500, detail=f"Failed to stop container: {exc}") from exc


@router.post('/docker/{container_id}/start')
def start_container(container_id: str):
    client = _get_client_or_400()
    try:
        container = client.containers.get(container_id)
    except NotFound:
        raise HTTPException(status_code=404, detail='Container not found')
    except DockerException:
        raise HTTPException(status_code=503, detail='Docker engine unavailable')
    try:
        container.start()
        return {"success": True, "message": "Container started successfully"}
    except DockerException as exc:
        raise HTTPException(status_code=500, detail=f"Failed to start container: {exc}") from exc


@router.delete('/docker/{container_id}')
def remove_container(container_id: str):
    client = _get_client_or_400()
    try:
        container = client.containers.get(container_id)
    except NotFound:
        raise HTTPException(status_code=404, detail='Container not found')
    except DockerException:
        raise HTTPException(status_code=503, detail='Docker engine unavailable')
    try:
        container.remove(force=True)
        return {"success": True, "message": "Container removed successfully"}
    except DockerException as exc:
        raise HTTPException(status_code=500, detail=f"Failed to remove container: {exc}") from exc
