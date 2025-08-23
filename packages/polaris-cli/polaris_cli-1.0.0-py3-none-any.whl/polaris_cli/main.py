#!/usr/bin/env python3
"""
Polaris CLI - Main entry point
"""

import sys
from typing import Optional

import typer
from polaris_cli.commands import (auth_commands, billing_commands,
                                  cluster_commands, config_commands,
                                  instance_commands, resource_commands,
                                  ssh_commands, status_commands,
                                  template_commands)
from polaris_cli.ui.banner import show_banner, show_version
from polaris_cli.utils.exceptions import PolarisError
from rich import print as rich_print
from rich.console import Console
from rich.text import Text

# Create the main Typer app
app = typer.Typer(
    name="polaris",
    help="Polariscloud resource management CLI",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Add command groups
app.add_typer(auth_commands.app, name="auth", help="Authentication and profile management")
app.add_typer(resource_commands.app, name="resources", help="Resource discovery and comparison")
app.add_typer(instance_commands.app, name="instances", help="Instance lifecycle management")
app.add_typer(cluster_commands.app, name="clusters", help="Cluster operations")
app.add_typer(template_commands.app, name="templates", help="Template management")
app.add_typer(ssh_commands.app, name="ssh", help="SSH access and key management")
app.add_typer(status_commands.app, name="status", help="System status and monitoring")
app.add_typer(billing_commands.app, name="billing", help="Billing and usage management")
app.add_typer(config_commands.app, name="config", help="Configuration management")

console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version information"),
    banner: bool = typer.Option(False, "--banner", help="Show banner"),
) -> None:
    """
    Polaris CLI - A beautiful cloud resource management interface.
    
    Get started:
    1. Set up authentication: polaris auth login --api-key YOUR_TOKEN
    2. Explore resources: polaris resources list
    3. Create instances: polaris instances create --help
    """
    if version:
        show_version()
        raise typer.Exit()
    
    if banner:
        show_banner()
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        show_banner()
        rich_print("\n[dim]Use [bold]polaris --help[/bold] to see available commands[/dim]")


def cli_main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except PolarisError as e:
        console.print(f"[red]Error:[/red] {e}", stderr=True)
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]", stderr=True)
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", stderr=True)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
