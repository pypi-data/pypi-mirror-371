"""
Configuration management commands
"""

from typing import Optional

import typer
from polaris_cli.config.manager import ConfigManager
from polaris_cli.ui.banner import show_error_message, show_success_message
from polaris_cli.ui.tables import show_table_with_panel
from polaris_cli.utils.exceptions import ConfigurationError
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Configuration management")
console = Console()


@app.command("show")
def show_config(
    profile: Optional[str] = typer.Option(None, "--profile", help="Show config for specific profile")
) -> None:
    """Show current configuration settings."""
    
    try:
        config_manager = ConfigManager()
        
        if profile:
            settings = config_manager.get_profile_config(profile)
            title = f"Configuration - Profile: {profile}"
        else:
            settings = config_manager.show_all()
            title = "Global Configuration"
        
        # Create configuration table
        table = Table(title=title, show_header=False)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        def add_settings_to_table(settings_dict, prefix=""):
            for key, value in settings_dict.items():
                full_key = f"{prefix}{key}" if prefix else key
                
                if isinstance(value, dict):
                    table.add_row(f"[bold]{full_key}[/bold]", "[dim]<section>[/dim]")
                    add_settings_to_table(value, f"{full_key}.")
                else:
                    if isinstance(value, bool):
                        value_str = "[green]true[/green]" if value else "[red]false[/red]"
                    elif isinstance(value, (int, float)):
                        value_str = f"[yellow]{value}[/yellow]"
                    elif value is None:
                        value_str = "[dim]null[/dim]"
                    else:
                        value_str = str(value)
                    
                    table.add_row(full_key, value_str)
        
        add_settings_to_table(settings)
        show_table_with_panel(table, f"Configuration loaded from ~/.polaris/")
        
    except ConfigurationError as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key (use dots for nested keys)"),
    value: str = typer.Argument(..., help="Configuration value"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Set for specific profile")
) -> None:
    """Set a configuration value."""
    
    try:
        config_manager = ConfigManager()
        
        # Try to parse value as appropriate type
        parsed_value = value
        if value.lower() in ("true", "false"):
            parsed_value = value.lower() == "true"
        elif value.isdigit():
            parsed_value = int(value)
        elif value.replace(".", "").isdigit():
            parsed_value = float(value)
        elif value.lower() == "null":
            parsed_value = None
        
        # Validate the setting
        if not config_manager.validate_setting(key, parsed_value):
            show_error_message(f"Invalid value '{value}' for setting '{key}'")
            raise typer.Exit(1)
        
        if profile:
            config_manager.set_profile_config(profile, key, parsed_value)
            show_success_message(f"Set '{key}' = '{parsed_value}' for profile '{profile}'")
        else:
            config_manager.set(key, parsed_value)
            show_success_message(f"Set '{key}' = '{parsed_value}'")
        
    except ConfigurationError as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("unset")
def unset_config(
    key: str = typer.Argument(..., help="Configuration key to remove"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Remove from specific profile")
) -> None:
    """Remove a configuration setting."""
    
    try:
        config_manager = ConfigManager()
        
        if profile:
            # For profile-specific removal, we'd need additional logic
            show_error_message("Profile-specific unset not yet implemented")
            raise typer.Exit(1)
        else:
            success = config_manager.unset(key)
            
            if success:
                show_success_message(f"Removed setting '{key}'")
            else:
                show_error_message(f"Setting '{key}' not found")
                raise typer.Exit(1)
        
    except ConfigurationError as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("reset")
def reset_config(
    profile: Optional[str] = typer.Option(None, "--profile", help="Reset specific profile")
) -> None:
    """Reset configuration to defaults."""
    
    if profile:
        confirm_msg = f"Are you sure you want to reset profile '{profile}' configuration?"
    else:
        confirm_msg = "Are you sure you want to reset all configuration to defaults?"
    
    confirm = typer.confirm(confirm_msg)
    if not confirm:
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    try:
        config_manager = ConfigManager()
        
        if profile:
            # Reset profile-specific config - would need implementation
            show_error_message("Profile-specific reset not yet implemented")
            raise typer.Exit(1)
        else:
            config_manager.reset()
            show_success_message("Configuration reset to defaults")
        
    except ConfigurationError as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("validate")
def validate_config() -> None:
    """Validate current configuration."""
    
    try:
        config_manager = ConfigManager()
        settings = config_manager.show_all()
        
        console.print("[cyan]Validating configuration...[/cyan]")
        
        errors = []
        warnings = []
        
        # Validate some common settings
        if settings.get("max_results", 0) > 1000:
            warnings.append("max_results is very high, this may cause performance issues")
        
        if settings.get("timeout", 0) < 10:
            warnings.append("timeout is very low, requests may fail frequently")
        
        if errors:
            console.print(f"\n[red]Errors found ({len(errors)}):[/red]")
            for error in errors:
                console.print(f"  • {error}")
        
        if warnings:
            console.print(f"\n[yellow]Warnings ({len(warnings)}):[/yellow]")
            for warning in warnings:
                console.print(f"  • {warning}")
        
        if not errors and not warnings:
            console.print("\n[green]✓ Configuration is valid[/green]")
        
    except ConfigurationError as e:
        show_error_message(str(e))
        raise typer.Exit(1)
