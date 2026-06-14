"""
AI DevOps Platform Monitoring Agent

A lightweight Python agent that collects system metrics (CPU, memory, disk usage)
and sends them to the central monitoring backend every 10 seconds.

Configuration:
    - Create a config.json file in the agent directory
    - Set BACKEND_URL: https://your-backend.com
    - Set API_KEY: Your agent API key from the dashboard

Usage:
    python agent.py [--config config.json]
"""

import os
import sys
import json
import logging
import argparse
import time
import socket
import platform
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

import psutil
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


# ==================== Configuration ====================

class AgentConfig:
    """Configuration management for the monitoring agent."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Load configuration from file or environment variables.
        
        Args:
            config_file: Path to JSON config file (optional)
        """
        self.config_file = config_file or "config.json"
        self.backend_url: str = ""
        self.api_key: str = ""
        self.interval_seconds: int = 10
        self.hostname: str = socket.gethostname()
        self.verify_ssl: bool = True
        self.timeout_seconds: int = 10
        self.max_retries: int = 3
        self.retry_backoff: float = 0.5
        self.log_level: str = "INFO"
        
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        # Try to load from config file first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._update_from_dict(file_config)
                    logging.getLogger(__name__).info(f"Loaded config from {self.config_file}")
            except Exception as e:
                logging.getLogger(__name__).warning(f"Failed to load config file: {e}")
        
        # Environment variables override file config
        if os.getenv("BACKEND_URL"):
            self.backend_url = os.getenv("BACKEND_URL")
        if os.getenv("API_KEY"):
            self.api_key = os.getenv("API_KEY")
        if os.getenv("INTERVAL_SECONDS"):
            self.interval_seconds = int(os.getenv("INTERVAL_SECONDS"))
        if os.getenv("AGENT_HOSTNAME"):
            self.hostname = os.getenv("AGENT_HOSTNAME")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary."""
        if "backend_url" in config_dict:
            self.backend_url = config_dict["backend_url"]
        if "api_key" in config_dict:
            self.api_key = config_dict["api_key"]
        if "interval_seconds" in config_dict:
            self.interval_seconds = int(config_dict["interval_seconds"])
        if "hostname" in config_dict:
            self.hostname = config_dict["hostname"]
        if "verify_ssl" in config_dict:
            self.verify_ssl = config_dict["verify_ssl"]
        if "timeout_seconds" in config_dict:
            self.timeout_seconds = int(config_dict["timeout_seconds"])
        if "max_retries" in config_dict:
            self.max_retries = int(config_dict["max_retries"])
        if "retry_backoff" in config_dict:
            self.retry_backoff = float(config_dict["retry_backoff"])
        if "log_level" in config_dict:
            self.log_level = config_dict["log_level"]
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        if not self.backend_url:
            raise ValueError("BACKEND_URL must be set in config file or environment variable")
        if not self.api_key:
            raise ValueError("API_KEY must be set in config file or environment variable")
        
        if not self.backend_url.startswith(("http://", "https://")):
            raise ValueError("BACKEND_URL must start with http:// or https://")


# ==================== Metrics Collection ====================

class MetricsCollector:
    """Collects system metrics from the local machine."""
    
    @staticmethod
    def collect() -> Dict[str, Any]:
        """
        Collect system metrics.
        
        Returns:
            Dictionary with CPU, memory, disk usage and system info
        """
        try:
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Get disk usage for root partition
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Get OS info
            os_name = platform.system()
            
            # Get hostname
            hostname = socket.gethostname()
            
            return {
                "hostname": hostname,
                "cpu_usage": round(cpu_usage, 2),
                "memory_usage": round(memory_usage, 2),
                "disk_usage": round(disk_usage, 2),
                "operating_system": os_name,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        except Exception as e:
            logging.getLogger(__name__).error(f"Error collecting metrics: {e}")
            raise


# ==================== HTTP Client ====================

class MetricsClient:
    """HTTP client for sending metrics to the backend with retry logic."""
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the HTTP client.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Send metrics to the backend.
        
        Args:
            metrics: Dictionary of metrics to send
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.config.backend_url.rstrip('/')}/agent/metrics/collect"
            
            headers = {
                "X-Agent-Key": self.config.api_key,
                "Content-Type": "application/json",
                "User-Agent": "AIDevOpsAgent/1.0"
            }
            
            response = self.session.post(
                url,
                json=metrics,
                headers=headers,
                timeout=self.config.timeout_seconds,
                verify=self.config.verify_ssl
            )
            
            # Check for success
            if response.status_code == 201:
                self.logger.debug(f"Metrics sent successfully: {metrics['hostname']}")
                return True
            elif response.status_code == 401:
                self.logger.error("Invalid API key - check your configuration")
                return False
            else:
                self.logger.warning(f"Server returned status {response.status_code}: {response.text}")
                return False
        
        except requests.exceptions.Timeout:
            self.logger.warning(f"Request timeout after {self.config.timeout_seconds}s")
            return False
        except requests.exceptions.ConnectionError as e:
            self.logger.warning(f"Connection error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending metrics: {e}")
            return False
    
    def close(self):
        """Close the session."""
        self.session.close()


# ==================== Main Agent ====================

class MonitoringAgent:
    """Main monitoring agent that runs in a loop."""
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = MetricsClient(config)
        self.running = False
        self.metrics_sent = 0
        self.metrics_failed = 0
    
    def run(self):
        """Run the agent in a loop."""
        self.running = True
        self.logger.info("Starting monitoring agent...")
        self.logger.info(f"Sending metrics to: {self.config.backend_url}")
        self.logger.info(f"Interval: {self.config.interval_seconds} seconds")
        self.logger.info(f"Hostname: {self.config.hostname}")
        
        try:
            while self.running:
                try:
                    # Collect metrics
                    metrics = MetricsCollector.collect()
                    
                    # Send metrics
                    if self.client.send_metrics(metrics):
                        self.metrics_sent += 1
                    else:
                        self.metrics_failed += 1
                    
                    # Wait for next interval
                    time.sleep(self.config.interval_seconds)
                
                except KeyboardInterrupt:
                    self.logger.info("Agent interrupted by user")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error in main loop: {e}")
                    self.metrics_failed += 1
                    time.sleep(self.config.interval_seconds)
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the agent gracefully."""
        self.running = False
        self.client.close()
        
        self.logger.info("Agent stopped")
        self.logger.info(f"Total metrics sent: {self.metrics_sent}")
        self.logger.info(f"Total failures: {self.metrics_failed}")


def setup_logging(log_level: str):
    """Set up logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('agent.log', mode='a')
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI DevOps Platform Monitoring Agent"
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = AgentConfig(args.config)
        
        # Set up logging
        setup_logging(config.log_level)
        logger = logging.getLogger(__name__)
        
        logger.info("AI DevOps Monitoring Agent v1.0")
        
        # Create and run agent
        agent = MonitoringAgent(config)
        agent.run()
    
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("\nConfiguration Example (config.json):")
        print(json.dumps({
            "backend_url": "https://your-backend.com",
            "api_key": "your_api_key_here",
            "interval_seconds": 10,
            "verify_ssl": True
        }, indent=2))
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
