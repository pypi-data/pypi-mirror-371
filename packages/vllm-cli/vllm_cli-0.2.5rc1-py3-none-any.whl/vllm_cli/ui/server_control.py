#!/usr/bin/env python3
"""
Server control module for vLLM CLI.

Handles server configuration and startup operations.
"""
import logging
import time
from typing import Any, Dict

import inquirer
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.padding import Padding
from rich.rule import Rule
from rich.text import Text

from ..config import ConfigManager
from ..server import VLLMServer
from ..system import get_gpu_info
from .common import console, create_panel
from .display import display_config, select_profile
from .gpu_utils import calculate_gpu_panel_size, create_gpu_status_panel
from .log_viewer import show_log_menu
from .model_manager import select_model
from .navigation import unified_prompt

logger = logging.getLogger(__name__)


def handle_quick_serve() -> str:
    """
    Quick serve with shortcuts or last used configuration.
    """
    from .shortcuts import serve_with_shortcut

    config_manager = ConfigManager()

    # Build quick serve options
    options = []

    # Add last config if available
    last_config = config_manager.get_last_config()
    if last_config:
        model_name = last_config.get("model", "unknown")
        if isinstance(model_name, dict):
            model_name = model_name.get("model", "unknown")
        # Truncate long model names
        if len(str(model_name)) > 40:
            model_display = "..." + str(model_name)[-37:]
        else:
            model_display = str(model_name)
        options.append(f"Last Config: {model_display}")

    # Add shortcuts
    # Get recent shortcuts first (those with last_used timestamps)
    recent_shortcuts = config_manager.get_recent_shortcuts(5)

    # If we have fewer than 5 recent shortcuts, supplement with unused ones
    if len(recent_shortcuts) < 5:
        all_shortcuts = config_manager.list_shortcuts()
        # Filter out the ones we already have in recent
        recent_names = {s["name"] for s in recent_shortcuts}
        unused_shortcuts = [s for s in all_shortcuts if s["name"] not in recent_names]
        # Add unused shortcuts to fill up to 10 total
        shortcuts = recent_shortcuts + unused_shortcuts[: 10 - len(recent_shortcuts)]
    else:
        shortcuts = recent_shortcuts

    if shortcuts:
        if options:  # If we have last config, add separator
            options.append("───────── Shortcuts ─────────")
        for shortcut in shortcuts:
            name = shortcut["name"]
            model = shortcut["model"]
            profile = shortcut["profile"]
            # Truncate long model names
            if len(str(model)) > 30:
                model_display = "..." + str(model)[-27:]
            else:
                model_display = str(model)
            options.append(f"{name}: {model_display} [{profile}]")

    # If no options available
    if not options:
        console.print("[yellow]No quick serve options available.[/yellow]")
        console.print("Please create shortcuts or use 'Serve with Profile' first.")
        input("\nPress Enter to continue...")
        return "continue"

    # Show quick serve menu
    console.print("\n[bold cyan]Quick Serve Options[/bold cyan]")
    selected = unified_prompt(
        "quick_serve", "Select configuration to launch", options, allow_back=True
    )

    if selected == "BACK" or not selected:
        return "continue"

    # Handle selection
    if selected.startswith("Last Config:"):
        # Serve with last config
        # Apply dynamic defaults for display
        profile_manager = config_manager.profile_manager
        config_with_defaults = profile_manager.apply_dynamic_defaults(last_config)

        # Show last configuration
        display_config(config_with_defaults, title="Last Configuration")

        # Confirm
        console.print()  # Add blank line for spacing
        confirm = inquirer.confirm(
            "Start server with this configuration?", default=True
        )

        if confirm:
            return start_server_with_config(config_with_defaults)

    elif (
        ":" in selected and "[" in selected and not selected.startswith("Last Config:")
    ):
        # Extract shortcut name from the selection
        # Format is "ShortcutName: model [profile]"
        shortcut_name = selected.split(":")[0].strip()
        return serve_with_shortcut(shortcut_name)

    return "continue"


def handle_serve_with_profile() -> str:
    """
    Serve a model with a pre-configured profile.
    """
    # Select model (can return string or dict with LoRA config)
    model_selection = select_model()
    if not model_selection:
        return "continue"

    # Handle different model selection formats
    lora_modules = None
    if isinstance(model_selection, dict):
        if "type" in model_selection and model_selection["type"] == "shortcut":
            # Shortcut selected - use its model and profile directly
            model = model_selection["model"]
            profile_name = model_selection["profile"]
            shortcut_name = model_selection["name"]
            config_overrides = model_selection.get("config_overrides", {})
            model_config = None

            console.print(f"\n[bold cyan]Using Shortcut: {shortcut_name}[/bold cyan]")
            console.print(f"  Model: {model}")
            console.print(f"  Profile: {profile_name}")

            # Skip profile selection since shortcut includes it
        elif "type" in model_selection and model_selection["type"] == "ollama_model":
            # Ollama/GGUF model configuration
            model = model_selection["model"]  # Path to GGUF file
            model_config = model_selection  # Keep full config for GGUF setup
            logger.info(f"Selected Ollama model: {model_selection.get('name', model)}")

            # Select profile for non-shortcut
            profile_name = select_profile()
            if not profile_name:
                return "continue"
        elif "lora_modules" in model_selection:
            # LoRA configuration
            model = model_selection["model"]
            lora_modules = model_selection["lora_modules"]
            model_config = model_selection

            # Select profile for non-shortcut
            profile_name = select_profile()
            if not profile_name:
                return "continue"
        else:
            # Other dict format - use as is
            model = model_selection.get("model", model_selection)
            model_config = model_selection

            # Select profile for non-shortcut
            profile_name = select_profile()
            if not profile_name:
                return "continue"
    else:
        # Simple string model name
        model = model_selection
        model_config = None

        # Select profile for non-shortcut
        profile_name = select_profile()
        if not profile_name:
            return "continue"

    # Get profile configuration
    config_manager = ConfigManager()
    profile = config_manager.get_profile(profile_name)
    if not profile:
        console.print(f"[red]Profile '{profile_name}' not found.[/red]")
        return "continue"

    config = profile.get("config", {}).copy()

    # Include environment variables from the profile
    profile_env = profile.get("environment", {})
    if profile_env:
        config["profile_environment"] = profile_env

    # If we have LoRA modules, update the config
    if model_config:
        config["model"] = model_config  # Pass the full dict with LoRA info
    else:
        config["model"] = model

    # Apply config overrides from shortcut if present
    if isinstance(model_selection, dict) and model_selection.get("type") == "shortcut":
        config_overrides = model_selection.get("config_overrides", {})
        if config_overrides:
            config.update(config_overrides)

    # Apply dynamic defaults for display
    profile_manager = config_manager.profile_manager
    config_with_defaults = profile_manager.apply_dynamic_defaults(config)

    # Show configuration
    display_config(config_with_defaults, title="Profile Configuration")

    # Get universal environment variables to show complete picture
    universal_env = config_manager.config.get("universal_environment", {})

    # Show environment variables with their sources
    total_env_vars = {}
    env_sources = {}

    # Add universal variables
    for key, value in universal_env.items():
        total_env_vars[key] = value
        env_sources[key] = "universal"

    # Add/override with profile variables
    for key, value in profile_env.items():
        total_env_vars[key] = value
        env_sources[key] = (
            "profile" if key not in universal_env else "profile (overrides universal)"
        )

    # Show environment variables if present
    if total_env_vars:
        console.print(f"\n[cyan]Environment Variables ({len(total_env_vars)}):[/cyan]")
        for key, value in total_env_vars.items():
            source = env_sources[key]
            # Hide sensitive values
            if "KEY" in key.upper() or "TOKEN" in key.upper():
                console.print(f"  • {key}: <hidden> [dim]({source})[/dim]")
            else:
                console.print(f"  • {key}: {value} [dim]({source})[/dim]")

    # Show LoRA adapters if present
    if lora_modules:
        console.print(f"\n[cyan]LoRA Adapters ({len(lora_modules)}):[/cyan]")
        for lora in lora_modules:
            name = lora.get("name", "unknown")
            rank = lora.get("rank", 16)
            path = lora.get("path", "")
            console.print(f"  • {name} (rank={rank})")
            console.print(f"    Path: {path}")

    # Confirm and start
    console.print()  # Add blank line for spacing
    confirm = inquirer.confirm("Start server with this configuration?", default=True)

    if confirm:
        # Save as last config
        config_manager.save_last_config(config_with_defaults)

        return start_server_with_config(config_with_defaults)

    return "continue"


def handle_custom_config() -> str:
    """
    Create a custom configuration for serving using category-based approach.
    """
    from .custom_config import configure_by_categories

    # Select model (can return string or dict with LoRA config)
    model_selection = select_model()
    if not model_selection:
        return "continue"

    # Handle different model selection formats
    lora_modules = None
    if isinstance(model_selection, dict):
        if "type" in model_selection and model_selection["type"] == "ollama_model":
            # Ollama/GGUF model configuration
            model = model_selection["model"]  # Path to GGUF file
            model_config = model_selection  # Keep full config for GGUF setup
            logger.info(f"Selected Ollama model: {model_selection.get('name', model)}")
        elif "lora_modules" in model_selection:
            # LoRA configuration
            model = model_selection["model"]
            lora_modules = model_selection["lora_modules"]
            model_config = model_selection
        else:
            # Other dict format - use as is
            model = model_selection.get("model", model_selection)
            model_config = model_selection
    else:
        # Simple string model name
        model = model_selection
        model_config = None

    console.print("\n[bold cyan]Custom Configuration[/bold cyan]")

    # Use category-based configuration
    config = configure_by_categories({"model": model})

    # Handle session environment variables if configured
    session_env = config.pop("session_environment", {})
    if session_env:
        # Store as profile_environment for the server to use
        config["profile_environment"] = session_env

    # If we have LoRA modules, update the config
    if model_config:
        config["model"] = model_config  # Pass the full dict with LoRA info
    else:
        config["model"] = model

    # Apply dynamic defaults for display
    config_manager = ConfigManager()
    profile_manager = config_manager.profile_manager
    config_with_defaults = profile_manager.apply_dynamic_defaults(config)

    # Show configuration summary
    display_config(config_with_defaults, title="Configuration Summary")

    # Show session environment variables if configured
    if session_env:
        console.print(
            f"\n[cyan]Session Environment Variables ({len(session_env)}):[/cyan]"
        )
        for key, value in session_env.items():
            if "KEY" in key.upper() or "TOKEN" in key.upper():
                console.print(f"  • {key}: <hidden>")
            else:
                console.print(f"  • {key}: {value}")

    # Show LoRA adapters if present
    if lora_modules:
        console.print(f"\n[cyan]LoRA Adapters ({len(lora_modules)}):[/cyan]")
        for lora in lora_modules:
            name = lora.get("name", "unknown")
            rank = lora.get("rank", 16)
            path = lora.get("path", "")
            console.print(f"  • {name} (rank={rank})")
            console.print(f"    Path: {path}")

    # Option to add raw custom vLLM arguments
    # Note: configure_by_categories already provides comprehensive configuration,
    # so we don't need to ask about customizing further
    console.print()  # Add blank line for spacing
    add_raw_args = inquirer.confirm("Add raw custom vLLM arguments?", default=False)

    if add_raw_args:
        console.print("\n[yellow]Custom vLLM Arguments[/yellow]")
        console.print(
            "Enter additional vLLM arguments exactly as you would on the command line."
        )
        console.print("Examples:")
        console.print("  --seed 42 --enable-prefix-caching")
        console.print("  --max-num-seqs 256 --disable-log-stats")
        console.print("  --lora-modules name=/path/to/lora")

        extra_args = input(
            "\nEnter custom arguments (or press Enter to skip): "
        ).strip()
        if extra_args:
            config["extra_args"] = extra_args
            console.print(f"[green]Custom arguments: {extra_args}[/green]")

    # Ask about saving configuration
    console.print()  # Add blank line for spacing
    save_profile = inquirer.confirm(
        "Save this configuration as a profile for future use?", default=False
    )

    profile_name = None
    if save_profile:
        profile_name = input("Profile name: ").strip()
        if profile_name:
            config_manager = ConfigManager()

            # Extract environment variables from config (stored as profile_environment)
            env_vars = config.pop("profile_environment", {})

            # Create clean config without environment variables
            clean_config = config.copy()
            clean_config.pop("model", None)  # Remove model from profile

            profile_data = {
                "name": profile_name,
                "description": "Custom configuration",
                "icon": "",
                "config": clean_config,  # Save config without model and environment
                "environment": env_vars,  # Save environment variables separately
                "lora_adapters": (
                    lora_modules if lora_modules else None
                ),  # Save LoRA adapter info if present
                "api_usage_info": config.get("api_usage_info"),  # Save API usage info
            }
            config_manager.save_user_profile(profile_name, profile_data)
            console.print(f"[green]✓ Profile '{profile_name}' saved.[/green]")
            if env_vars:
                console.print(
                    f"[green]  Including {len(env_vars)} environment variable(s)[/green]"
                )

            # Now ask about creating a shortcut
            console.print()  # Add blank line for spacing
            create_shortcut = inquirer.confirm(
                "Create a shortcut for quick launching this model+profile combination?",
                default=False,
            )

            if create_shortcut:
                shortcut_name = input("Shortcut name: ").strip()
                if shortcut_name:
                    shortcut_data = {
                        "model": model,
                        "profile": profile_name,
                        "description": f"Custom config for {model}",
                    }
                    if config_manager.save_shortcut(shortcut_name, shortcut_data):
                        console.print(
                            f"[green]✓ Shortcut '{shortcut_name}' created![/green]"
                        )
                        console.print(
                            f'[dim]Quick launch: vllm-cli serve --shortcut "{shortcut_name}"[/dim]'
                        )
                    else:
                        console.print("[red]Failed to create shortcut.[/red]")

    # Start server
    console.print()  # Add blank line for spacing
    confirm = inquirer.confirm("Start server with this configuration?", default=True)

    if confirm:
        config_manager = ConfigManager()
        config_manager.save_last_config(config_with_defaults)
        return start_server_with_config(config_with_defaults)

    return "continue"


def start_server_with_config(config: Dict[str, Any]) -> str:
    """
    Start vLLM server with given configuration.
    """
    from .server_monitor import monitor_server

    # Validate configuration before starting
    config_manager = ConfigManager()

    # Basic validation
    is_valid, errors = config_manager.validate_config(config)
    if not is_valid:
        console.print("[red]Configuration validation failed:[/red]")
        for error in errors:
            console.print(f"  • {error}")
        input("\nPress Enter to continue...")
        return "continue"

    # Compatibility validation
    is_compatible, warnings = config_manager.validate_argument_combination(config)
    if warnings:
        console.print("[yellow]Configuration warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")

        # For errors (severity), ask user if they want to continue
        if not is_compatible:
            console.print("\n[red]Some configuration conflicts were detected.[/red]")
            continue_anyway = inquirer.confirm(
                "Continue anyway? (The server may not work as expected)", default=False
            )
            if not continue_anyway:
                return "continue"

        console.print()  # Add spacing

    # Check if this is a remote model by checking if it exists locally
    model_config = config.get("model", "")

    # Extract model name from LoRA config if needed
    if isinstance(model_config, dict):
        model_name = model_config.get("model", "")
    else:
        model_name = model_config

    # Check if model exists in local cache
    from ..models import list_available_models

    local_models = list_available_models()
    local_model_names = [m.get("name", "") for m in local_models]

    # A model is remote if it has "/" (HuggingFace format) and is NOT in local cache
    is_remote_model = (
        "/" in model_name
        and not model_name.startswith("/")
        and model_name not in local_model_names
    )

    if is_remote_model:
        console.print(
            f"\n[bold cyan]Starting vLLM server with remote model:[/bold cyan] {model_name}"
        )
        console.print(
            "[yellow]Note: First-time use will download the model from HuggingFace Hub.[/yellow]"
        )
        console.print(
            "[dim]Download may take 10-30 minutes depending on size and connection speed.[/dim]\n"
        )
    else:
        console.print("\n[bold cyan]Starting vLLM server...[/bold cyan]")

    # Get UI preferences for configurable log lines and refresh rate
    ui_prefs = config_manager.get_ui_preferences()
    startup_refresh_rate = ui_prefs.get("startup_refresh_rate", 4.0)

    try:
        server = VLLMServer(config)

        # Start the server (this launches the process)
        server.start()

        # Give the log thread a moment to start
        time.sleep(0.2)  # Reduced delay since we fixed buffering

        # Get GPU info to calculate optimal panel size
        gpu_info = get_gpu_info()
        gpu_panel_size = calculate_gpu_panel_size(len(gpu_info) if gpu_info else 0)

        # Create a layout for showing startup progress
        layout = Layout()
        layout.split_column(
            Layout(name="status", size=3),
            Layout(name="gpu", size=gpu_panel_size),  # Dynamic size based on GPU count
            Layout(name="log_divider", size=1),
            Layout(name="logs"),  # Takes remaining space
            Layout(name="info", size=3),
            Layout(name="footer", size=1),
        )

        # Initial status
        layout["status"].update(
            create_panel(
                "[yellow]⠋ Starting vLLM server... This may take a few minutes for model loading.[/yellow]",
                title="Status",
                border_style="yellow",
            )
        )

        # Initial GPU panel
        layout["gpu"].update(create_gpu_status_panel())

        # Extract model name for display
        model_display = config.get("model", "unknown")
        if isinstance(model_display, dict):
            model_display = model_display.get("model", "unknown")

        layout["info"].update(
            create_panel(
                f"Port: {server.port} | Model: {model_display}",
                title="Info",
                border_style="blue",
            )
        )

        # Footer with exit instructions
        layout["footer"].update(
            Align.center(Text("Press Ctrl+C to cancel startup", style="dim yellow"))
        )

        startup_logs = []
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame_idx = 0
        startup_complete = False
        startup_failed = False
        no_log_count = 0  # Track how many times we've seen no logs

        # Monitor startup for up to 5 minutes
        startup_cancelled = False
        try:
            with Live(
                layout, console=console, refresh_per_second=startup_refresh_rate
            ):  # User-configurable refresh rate
                start_time = time.time()

                while not startup_complete and not startup_failed:
                    # Check if server is still running first
                    if not server.is_running():
                        startup_failed = True
                        layout["status"].update(
                            create_panel(
                                "[red]✗ Server process terminated unexpectedly[/red]",
                                title="Status",
                                border_style="red",
                            )
                        )
                        break

                    # Get recent logs
                    new_logs = server.get_recent_logs(50)
                    if new_logs:
                        startup_log_lines = ui_prefs.get("log_lines_startup", 50)
                        startup_logs = new_logs[
                            -startup_log_lines:
                        ]  # Keep configurable number of lines for display
                        no_log_count = 0  # Reset counter when we get logs

                        # Check for startup completion indicators
                        for log in new_logs:
                            log_lower = log.lower()
                            # vLLM ready indicators
                            if any(
                                indicator in log_lower
                                for indicator in [
                                    "uvicorn running on",
                                    "started server process",
                                    "application startup complete",
                                    "server is ready",
                                    "api server started",
                                ]
                            ):
                                startup_complete = True
                                break
                            # Check for critical errors (not warnings)
                            elif "traceback" in log or "error:" in log_lower:
                                # Look for actual error patterns, not just the word "error"
                                if any(
                                    err in log_lower
                                    for err in [
                                        "cuda out of memory",
                                        "failed to load",
                                        "no such file",
                                        "permission denied",
                                        "address already in use",
                                        "cuda error",
                                        "runtime error",
                                        "value error",
                                        "import error",
                                    ]
                                ):
                                    startup_failed = True
                                    break
                    else:
                        no_log_count += 1

                    # Update spinner
                    frame_idx = (frame_idx + 1) % len(spinner_frames)
                    spinner = spinner_frames[frame_idx]

                    # Update GPU panel periodically
                    if (
                        frame_idx % 4 == 0
                    ):  # Update every 4th frame (about once per second)
                        layout["gpu"].update(create_gpu_status_panel())

                    # Update status based on logs
                    if not startup_complete and not startup_failed:
                        elapsed = int(time.time() - start_time)
                        status_msg = (
                            f"{spinner} Starting vLLM server... ({elapsed}s elapsed)"
                        )

                        # Try to detect what stage we're in from logs
                        # stage_detected = False  # Not used
                        for log in reversed(startup_logs):  # Check most recent first
                            log_lower = log.lower()
                            if (
                                "loading weights" in log_lower
                                or "loading model" in log_lower
                            ):
                                status_msg = f"{spinner} Loading model weights... This may take a while ({elapsed}s)"
                                # stage_detected = True  # Not needed
                                break
                            elif "initializing" in log_lower and "engine" in log_lower:
                                status_msg = f"{spinner} Initializing vLLM engine... ({elapsed}s)"
                                # stage_detected = True  # Not needed
                                break
                            elif "compiling" in log_lower or "cuda graph" in log_lower:
                                status_msg = f"{spinner} Compiling CUDA kernels and graphs... ({elapsed}s)"
                                # stage_detected = True  # Not needed
                                break
                            elif "downloading" in log_lower or "fetching" in log_lower:
                                # Try to extract download progress if available
                                progress_info = ""
                                if "%" in log:
                                    # Try to extract percentage
                                    import re

                                    match = re.search(r"(\d+(?:\.\d+)?)\s*%", log)
                                    if match:
                                        progress_info = f" - {match.group(1)}%"

                                status_msg = f"{spinner} Downloading model from HuggingFace Hub{progress_info}... ({elapsed}s)"
                                # stage_detected = True  # Not needed
                                break
                            elif (
                                "starting server" in log_lower
                                or "starting uvicorn" in log_lower
                            ):
                                status_msg = f"{spinner} Starting API server... Almost ready! ({elapsed}s)"
                                # stage_detected = True  # Not needed
                                break

                        layout["status"].update(
                            create_panel(
                                f"[yellow]{status_msg}[/yellow]",
                                title="Status",
                                border_style="yellow",
                            )
                        )

                    # Update log divider
                    if startup_logs:
                        layout["log_divider"].update(
                            Rule(
                                f"Startup Logs (Last {len(startup_logs)} lines)",
                                style="cyan",
                            )
                        )
                    else:
                        layout["log_divider"].update(Rule("Startup Logs", style="cyan"))

                    # Update logs (no panel, just text)
                    if startup_logs:
                        log_text = Text("\n".join(startup_logs), style="dim white")
                        layout["logs"].update(Padding(log_text, (0, 2)))
                    else:
                        # Show different messages based on how long we've been waiting
                        if no_log_count < 2:
                            msg = f"{spinner} Initializing vLLM server..."
                        elif no_log_count < 8:
                            msg = f"{spinner} Starting vLLM process..."
                        else:
                            msg = f"{spinner} Still waiting for vLLM output... Check if vLLM is installed and in your PATH."

                        log_text = Text(msg, style="dim yellow")
                        layout["logs"].update(Padding(log_text, (0, 2)))

                    time.sleep(0.25)  # Reduced sleep for faster updates
        except KeyboardInterrupt:
            startup_cancelled = True
            console.print("\n[yellow]Startup cancelled by user.[/yellow]")

        # Show final status
        if startup_cancelled:
            console.print("[yellow]Server startup was cancelled.[/yellow]")
            console.print("")
            console.print(
                "[bold]Do you want to stop the server process?[/bold] [dim](Y/n):[/dim] ",
                end="",
            )
            response = input().strip().lower()
            if response != "n" and response != "no":
                console.print("[yellow]Stopping server...[/yellow]")
                server.stop()
                console.print("[green]✓ Server stopped.[/green]")
            else:
                console.print("[dim]Server process continues in background.[/dim]")
                console.print(
                    "[yellow]⚠ Warning: You will not be able to monitor server logs from vLLM CLI[/yellow]"
                )
                console.print(
                    f"[dim]Note: Server may still be starting up. Check port {server.port}[/dim]"
                )
        elif startup_complete:
            console.print(
                f"[green]✓ Server successfully started on port {server.port}[/green]"
            )
            console.print(
                f"[green]API endpoint: http://localhost:{server.port}[/green]"
            )

            # Option to monitor - use navigation system
            options = ["Monitor server output", "Return to main menu"]

            choice = unified_prompt(
                "post_startup", "What would you like to do?", options, allow_back=False
            )

            if choice == "Monitor server output":
                return monitor_server(server)
            else:
                console.print("[green]Server is running in background.[/green]")
        else:
            console.print("\n[red]✗ Failed to start server[/red]")
            if startup_logs:
                console.print("\n[bold]Last logs:[/bold]")
                for log in startup_logs[-5:]:
                    console.print(f"  {log}")
            # Offer to view logs interactively
            console.print(
                "\n[yellow]Server startup failed. Last logs shown above.[/yellow]"
            )

            view_logs = (
                input("\nWould you like to view the full logs? (y/N): ").strip().lower()
            )
            if view_logs in ["y", "yes"]:
                show_log_menu(server)
            else:
                console.print(f"\n[dim]Full log file: {server.log_path}[/dim]")

    except Exception as e:
        logger.error(f"Error starting server: {e}")
        console.print(f"[red]Error starting server: {e}[/red]")

    input("\nPress Enter to continue...")
    return "continue"
