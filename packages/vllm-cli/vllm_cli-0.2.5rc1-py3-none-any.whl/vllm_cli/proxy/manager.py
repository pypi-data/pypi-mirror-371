#!/usr/bin/env python3
"""
Manager for coordinating multiple vLLM server instances and the proxy server.
"""
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import ConfigManager
from ..server import VLLMServer
from ..server.utils import get_next_available_port
from .models import ModelConfig, ProxyConfig
from .server_process import ProxyServerProcess

logger = logging.getLogger(__name__)


class ProxyManager:
    """
    Manages the lifecycle of multiple vLLM servers and the proxy server.
    """

    def __init__(self, config: Optional[ProxyConfig] = None):
        """
        Initialize the proxy manager.

        Args:
            config: Proxy configuration (uses defaults if not provided)
        """
        self.proxy_config = config or ProxyConfig()
        self.proxy_process: Optional[ProxyServerProcess] = None
        self.vllm_servers: Dict[str, VLLMServer] = {}
        self.config_manager = ConfigManager()

    def _proxy_api_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        timeout: float = 5.0,
    ) -> Optional[Any]:
        """
        Helper method for making HTTP requests to the proxy API.

        Args:
            method: HTTP method (POST, DELETE, GET)
            endpoint: API endpoint path
            json_data: Optional JSON data for request body
            timeout: Request timeout in seconds

        Returns:
            Response object if successful, None if failed
        """
        try:
            import httpx

            url = f"http://localhost:{self.proxy_config.port}{endpoint}"
            with httpx.Client() as client:
                if method == "POST":
                    response = client.post(url, json=json_data, timeout=timeout)
                elif method == "DELETE":
                    response = client.delete(url, timeout=timeout)
                elif method == "GET":
                    response = client.get(url, timeout=timeout)
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return None

                if response.status_code == 200:
                    return response
                else:
                    logger.warning(
                        f"API request failed: {method} {endpoint} - "
                        f"{response.status_code}: {response.text}"
                    )
                    return None

        except Exception as e:
            logger.warning(f"API request error: {method} {endpoint} - {e}")
            return None

    def start_proxy(self) -> bool:
        """
        Start the proxy server.

        Returns:
            True if proxy started successfully
        """
        try:
            # Create proxy server process instance
            self.proxy_process = ProxyServerProcess(self.proxy_config)

            # Start proxy as a subprocess
            if not self.proxy_process.start():
                logger.error("Failed to start proxy server process")
                return False

            # Give it a moment to fully initialize
            time.sleep(2)

            # Register all running models with the proxy
            # Note: We'll need to update this to work with subprocess
            # For now, models will register when they start

            logger.info(
                f"Proxy server started on "
                f"{self.proxy_config.host}:{self.proxy_config.port}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start proxy server: {e}")
            return False

    def stop_proxy(self):
        """Stop the proxy server and all vLLM instances."""
        logger.info("Stopping proxy server and all model servers...")

        # Stop all vLLM servers
        for model_name in list(self.vllm_servers.keys()):
            self.stop_model(model_name)

        # Stop proxy server process
        if self.proxy_process:
            self.proxy_process.stop()
            self.proxy_process = None
            logger.info("Proxy server stopped")

    def start_model(self, model_config: ModelConfig) -> bool:
        """
        Start a vLLM server for a specific model.

        Args:
            model_config: Configuration for the model

        Returns:
            True if server started successfully
        """
        try:
            # Check if model is already running
            if model_config.name in self.vllm_servers:
                logger.warning(f"Model '{model_config.name}' is already running")
                return False

            # Build vLLM server configuration
            vllm_config = self._build_vllm_config(model_config)

            # Create and start vLLM server
            server = VLLMServer(vllm_config)
            if not server.start():
                logger.error(f"Failed to start vLLM server for '{model_config.name}'")
                return False

            # Store server reference
            self.vllm_servers[model_config.name] = server

            logger.info(
                f"Started vLLM server process for '{model_config.name}' "
                f"on port {model_config.port} using GPUs {model_config.gpu_ids}"
            )

            # Note: Registration with proxy will happen after startup completes
            # This is handled by wait_and_register_model() from start_all_models()

            return True

        except Exception as e:
            logger.error(f"Failed to start model '{model_config.name}': {e}")
            return False

    def wait_and_register_model(self, model_config: ModelConfig) -> bool:
        """
        Wait for a model to complete startup and register it with the proxy.

        Args:
            model_config: Configuration for the model

        Returns:
            True if model started and registered successfully
        """
        if model_config.name not in self.vllm_servers:
            logger.error(f"Model '{model_config.name}' not found in servers")
            return False

        server = self.vllm_servers[model_config.name]

        # Wait for server to complete startup
        if not server.wait_for_startup():
            logger.error(f"Server '{model_config.name}' failed to complete startup")
            # Clean up the failed server
            server.stop()
            del self.vllm_servers[model_config.name]
            return False

        # Register with proxy if it's running
        if self.proxy_process and self.proxy_process.is_running():
            # Prepare model configuration for proxy
            model_data = {
                "name": model_config.name,
                "port": model_config.port,
                "model_path": model_config.model_path,
                "gpu_ids": model_config.gpu_ids,
                **model_config.config_overrides,
            }

            # Register model with proxy via HTTP API
            if self._proxy_api_request("POST", "/proxy/add_model", model_data):
                logger.debug(f"Registered model '{model_config.name}' with proxy")

                # Also register any aliases
                aliases = model_config.config_overrides.get("aliases", [])
                for alias in aliases:
                    alias_data = model_data.copy()
                    alias_data["name"] = alias
                    if self._proxy_api_request("POST", "/proxy/add_model", alias_data):
                        logger.debug(f"Registered alias '{alias}' with proxy")

        logger.info(f"Model '{model_config.name}' is ready and registered")
        return True

    def stop_model(self, model_name: str) -> bool:
        """
        Stop a vLLM server for a specific model.

        Args:
            model_name: Name of the model to stop

        Returns:
            True if server stopped successfully
        """
        if model_name not in self.vllm_servers:
            logger.warning(f"Model '{model_name}' is not running")
            return False

        try:
            # Stop the vLLM server
            server = self.vllm_servers[model_name]
            server.stop()

            # Remove from tracking
            del self.vllm_servers[model_name]

            # Remove from proxy if it's running
            if self.proxy_process and self.proxy_process.is_running():
                # Remove main model from proxy
                if self._proxy_api_request(
                    "DELETE", f"/proxy/remove_model/{model_name}"
                ):
                    logger.debug(f"Removed model '{model_name}' from proxy")

                # Also remove any aliases
                model_config = self._get_model_config_by_name(model_name)
                if model_config:
                    aliases = model_config.config_overrides.get("aliases", [])
                    for alias in aliases:
                        if self._proxy_api_request(
                            "DELETE", f"/proxy/remove_model/{alias}"
                        ):
                            logger.debug(f"Removed alias '{alias}' from proxy")

            logger.info(f"Stopped vLLM server for '{model_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to stop model '{model_name}': {e}")
            return False

    def start_all_models(self) -> int:
        """
        Start all models defined in the proxy configuration.

        Returns:
            Number of models successfully started
        """
        # First, start all model processes concurrently
        started_configs = []
        for model_config in self.proxy_config.models:
            if model_config.enabled:
                if self.start_model(model_config):
                    started_configs.append(model_config)
                    # Small delay to avoid resource conflicts but not wait for startup
                    time.sleep(0.5)

        # Now wait for all started models to complete startup and register them
        successfully_started = 0
        for model_config in started_configs:
            if self.wait_and_register_model(model_config):
                successfully_started += 1

        return successfully_started

    def start_all_models_no_wait(self) -> int:
        """
        Start all model processes without waiting for startup completion.

        This method starts all model servers concurrently and returns immediately,
        allowing the caller to monitor startup progress in real-time.

        Returns:
            Number of model processes successfully launched
        """
        started_count = 0
        for model_config in self.proxy_config.models:
            if model_config.enabled:
                if self.start_model(model_config):
                    started_count += 1
                    # Small delay to avoid resource conflicts
                    time.sleep(0.5)

        return started_count

    def _build_vllm_config(self, model_config: ModelConfig) -> Dict[str, Any]:
        """
        Build vLLM server configuration from model configuration.

        Args:
            model_config: Model configuration

        Returns:
            vLLM server configuration dictionary
        """
        # Start with profile configuration if specified
        config = {}
        if model_config.profile:
            profile = self.config_manager.get_profile(model_config.profile)
            if profile:
                config = profile.get("config", {}).copy()

        # Set model and port
        config["model"] = model_config.model_path
        config["port"] = model_config.port

        # Handle GPU assignment
        if model_config.gpu_ids:
            # Set CUDA_VISIBLE_DEVICES via device field
            config["device"] = ",".join(str(gpu) for gpu in model_config.gpu_ids)

            num_gpus = len(model_config.gpu_ids)

            # For single GPU assignment, override any parallel settings from profile
            if num_gpus == 1:
                # Remove parallel configuration that conflicts with single GPU
                conflicting_settings = [
                    "tensor_parallel_size",
                    "pipeline_parallel_size",
                    "distributed_executor_backend",
                ]

                removed_settings = []
                for setting in conflicting_settings:
                    if setting in config:
                        removed_settings.append(f"{setting}={config[setting]}")
                        del config[setting]

                # Disable expert parallelism for single GPU
                if config.get("enable_expert_parallel"):
                    removed_settings.append("enable_expert_parallel=True")
                    config["enable_expert_parallel"] = False

                if removed_settings:
                    logger.warning(
                        f"Model '{model_config.name}' assigned single GPU. "
                        f"Overriding profile settings: {', '.join(removed_settings)}"
                    )

            elif num_gpus > 1:
                # For multi-GPU, set tensor_parallel_size if not already set
                if "tensor_parallel_size" not in config:
                    config["tensor_parallel_size"] = num_gpus
                elif config["tensor_parallel_size"] > num_gpus:
                    # Adjust if profile expects more GPUs than assigned
                    logger.warning(
                        f"Model '{model_config.name}': Adjusting tensor_parallel_size "
                        f"from {config['tensor_parallel_size']} to {num_gpus} "
                        f"(assigned GPUs)"
                    )
                    config["tensor_parallel_size"] = num_gpus

        # Apply any config overrides
        config.update(model_config.config_overrides)

        return config

    def get_status(self) -> Dict[str, Any]:
        """
        Get status of proxy and all model servers.

        Returns:
            Status dictionary
        """
        status = {
            "proxy_running": self.proxy_process and self.proxy_process.is_running(),
            "proxy_host": self.proxy_config.host,
            "proxy_port": self.proxy_config.port,
            "models": [],
        }

        for model_name, server in self.vllm_servers.items():
            model_status = {
                "name": model_name,
                "running": server.is_running(),
                "port": server.port,
                "uptime": None,
            }

            if server.is_running() and server.start_time:
                uptime = time.time() - server.start_time.timestamp()
                model_status["uptime"] = uptime

            status["models"].append(model_status)

        return status

    def reload_model(self, model_name: str) -> bool:
        """
        Reload a model (stop and start again).

        Args:
            model_name: Name of the model to reload

        Returns:
            True if reload successful
        """
        # Find the model config
        model_config = None
        for config in self.proxy_config.models:
            if config.name == model_name:
                model_config = config
                break

        if not model_config:
            logger.error(f"Model '{model_name}' not found in configuration")
            return False

        # Stop if running
        if model_name in self.vllm_servers:
            self.stop_model(model_name)
            time.sleep(2)  # Wait before restarting

        # Start the model
        if not self.start_model(model_config):
            return False

        # Wait for startup and register
        return self.wait_and_register_model(model_config)

    def allocate_gpus_automatically(self) -> List[ModelConfig]:
        """
        Automatically allocate GPUs to models based on available resources.

        Returns:
            List of model configurations with GPU allocations
        """
        from ..system import get_gpu_info

        # Get available GPUs
        gpu_info = get_gpu_info()
        if not gpu_info:
            logger.warning("No GPUs available for allocation")
            return []

        num_gpus = len(gpu_info)
        models = self.proxy_config.models

        # Simple allocation strategy: distribute GPUs evenly
        allocated_configs = []

        if len(models) <= num_gpus:
            # Each model gets at least one GPU
            gpus_per_model = num_gpus // len(models)
            remaining_gpus = num_gpus % len(models)

            gpu_index = 0
            for i, model in enumerate(models):
                num_gpus_for_model = gpus_per_model
                if i < remaining_gpus:
                    num_gpus_for_model += 1

                model.gpu_ids = list(range(gpu_index, gpu_index + num_gpus_for_model))
                gpu_index += num_gpus_for_model

                # Allocate port if not specified
                if not model.port:
                    model.port = get_next_available_port(8001 + i)

                allocated_configs.append(model)
        else:
            # More models than GPUs - some models won't be allocated
            logger.warning(
                f"More models ({len(models)}) than GPUs ({num_gpus}). "
                f"Only first {num_gpus} models will be allocated."
            )
            for i in range(num_gpus):
                models[i].gpu_ids = [i]
                if not models[i].port:
                    models[i].port = get_next_available_port(8001 + i)
                allocated_configs.append(models[i])

        return allocated_configs

    def _get_model_config_by_name(self, model_name: str) -> Optional[ModelConfig]:
        """
        Get model configuration by model name.

        Args:
            model_name: Name of the model

        Returns:
            ModelConfig if found, None otherwise
        """
        for model_config in self.proxy_config.models:
            if model_config.name == model_name:
                return model_config
        return None

    @classmethod
    def from_config_file(cls, config_path: Path) -> "ProxyManager":
        """
        Create ProxyManager from a configuration file.

        Args:
            config_path: Path to configuration file (YAML or JSON)

        Returns:
            ProxyManager instance
        """
        import json

        import yaml

        with open(config_path, "r") as f:
            if config_path.suffix in [".yaml", ".yml"]:
                config_dict = yaml.safe_load(f)
            else:
                config_dict = json.load(f)

        # Parse proxy configuration
        proxy_config = ProxyConfig(**config_dict.get("proxy", {}))

        # Parse model configurations
        models = []
        for model_dict in config_dict.get("models", []):
            models.append(ModelConfig(**model_dict))
        proxy_config.models = models

        return cls(proxy_config)
