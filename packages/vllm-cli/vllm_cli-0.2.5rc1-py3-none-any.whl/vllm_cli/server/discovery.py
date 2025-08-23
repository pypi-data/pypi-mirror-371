#!/usr/bin/env python3
"""
External vLLM server discovery utilities.

Scans system processes to detect vLLM servers that were started
independently of this CLI tool.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def detect_running_vllm_servers() -> List[Dict[str, Any]]:
    """
    Detect vLLM servers running outside of this CLI.

    Scans system processes to find running vLLM servers that were
    started independently of this CLI tool. Extracts model names
    and port numbers from command line arguments when possible.

    Returns:
        List of dictionaries containing detected server information
        with keys: 'pid', 'model', 'port'
    """
    try:
        return _scan_vllm_processes()
    except ImportError:
        logger.warning("psutil not available, cannot detect external vLLM servers")
        return []
    except Exception as e:
        logger.error(f"Error detecting vLLM servers: {e}")
        return []


def detect_external_servers():
    """Alias for detect_running_vllm_servers for backwards compatibility."""
    return detect_running_vllm_servers()


def _scan_vllm_processes() -> List[Dict[str, Any]]:
    """
    Scan system processes for running vLLM servers.

    Returns:
        List of server information dictionaries
    """
    import psutil

    servers = []

    for proc in psutil.process_iter(["pid", "name", "cmdline", "status"]):
        try:
            # Skip zombie or dead processes
            status = proc.info.get("status", "")
            if status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                logger.debug(f"Skipping zombie/dead process PID {proc.info['pid']}")
                continue

            # Double-check the process is actually running
            if not proc.is_running():
                logger.debug(f"Skipping non-running process PID {proc.info['pid']}")
                continue

            cmdline = proc.info.get("cmdline", [])
            if _is_vllm_serve_process(cmdline):
                server_info = _extract_server_info_from_cmdline(
                    proc.info["pid"], cmdline
                )
                servers.append(server_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return servers


def _is_vllm_serve_process(cmdline: List[str]) -> bool:
    """
    Check if a command line represents a vLLM serve process.

    Args:
        cmdline: Command line arguments list

    Returns:
        True if this is a vLLM serve process or proxy server
    """
    if not cmdline:
        return False

    cmdline_str = " ".join(cmdline).lower()

    # Check for regular vLLM serve process
    if "vllm" in cmdline_str and "serve" in cmdline_str:
        return True

    # Check for proxy server process
    if "vllm_cli.proxy.server_launcher" in cmdline_str:
        return True

    return False


def _extract_server_info_from_cmdline(pid: int, cmdline: List[str]) -> Dict[str, Any]:
    """
    Extract server information from vLLM command line arguments.

    Args:
        pid: Process ID
        cmdline: Command line arguments

    Returns:
        Dictionary with server information
    """
    server_info = {"pid": pid, "model": "unknown", "port": 8000}  # Default

    # Check if this is a proxy server
    cmdline_str = " ".join(cmdline)
    if "vllm_cli.proxy.server_launcher" in cmdline_str:
        server_info["model"] = "vLLM Proxy"
        # Extract port from proxy command line
        for i, arg in enumerate(cmdline):
            if arg == "--port" and i + 1 < len(cmdline):
                try:
                    server_info["port"] = int(cmdline[i + 1])
                except ValueError:
                    pass  # Keep default port
        return server_info

    # Try to extract model and port from regular vLLM command line
    for i, arg in enumerate(cmdline):
        if arg == "serve" and i + 1 < len(cmdline):
            server_info["model"] = cmdline[i + 1]
        elif arg == "--port" and i + 1 < len(cmdline):
            try:
                server_info["port"] = int(cmdline[i + 1])
            except ValueError:
                pass  # Keep default port

    return server_info
