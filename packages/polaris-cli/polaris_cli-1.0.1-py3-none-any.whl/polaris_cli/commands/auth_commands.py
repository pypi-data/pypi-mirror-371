"""
Authentication commands for Polaris CLI
"""

from typing import Optional

import typer
from polaris_cli.auth.token_manager import TokenManager
from polaris_cli.ui.banner import (show_error_message, show_loading_spinner,
                                   show_success_message)
from polaris_cli.ui.tables import format_status, show_table_with_panel
from polaris_cli.utils.exceptions import (AuthenticationError,
                                          ConfigurationError)
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Authentication and profile management")
console = Console()


@app.command("login")
def login(
    api_key: str = typer.Option(..., "--api-key", help="API key for authentication"),
    profile: str = typer.Option("default", "--profile", help="Profile name")
) -> None:
    """Login with an API key and save it to a profile."""
    
    console.print(f"[cyan]Logging in with profile '[bold]{profile}[/bold]'...[/cyan]")
    show_loading_spinner("Validating token", 1.5)
    
    try:
        token_manager = TokenManager()
        token_manager.login_with_token(api_key, profile)
        
        show_success_message(f"Successfully logged in as profile '{profile}'")
        console.print(f"\n[dim]Use [bold]polaris auth status[/bold] to verify authentication[/dim]")
        
    except AuthenticationError as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("logout")
def logout(
    profile: Optional[str] = typer.Option(None, "--profile", help="Profile name to logout")
) -> None:
    """Logout by removing the specified profile."""
    
    try:
        token_manager = TokenManager()
        
        if profile is None:
            status = token_manager.get_auth_status()
            profile = status.get("profile")
            
            if not profile:
                show_error_message("No active profile to logout")
                raise typer.Exit(1)
        
        console.print(f"[cyan]Logging out profile '[bold]{profile}[/bold]'...[/cyan]")
        token_manager.logout(profile)
        
        show_success_message(f"Successfully logged out profile '{profile}'")
        
    except (AuthenticationError, ConfigurationError) as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("status")
def status() -> None:
    """Show current authentication status."""
    
    try:
        token_manager = TokenManager()
        auth_status = token_manager.get_auth_status()
        
        if not auth_status["authenticated"]:
            console.print("[red]Not authenticated[/red]")
            console.print("\n[dim]Use [bold]polaris auth login --api-key YOUR_TOKEN[/bold] to login[/dim]")
            return
        
        # Create status table
        table = Table(title="Authentication Status", show_header=False)
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Status", "[green]✓ Authenticated[/green]")
        table.add_row("Profile", auth_status["profile"])
        table.add_row("Token", auth_status.get("token_prefix", "N/A"))
        
        # Add user info from JWT
        if auth_status.get("user_email"):
            table.add_row("User Email", auth_status["user_email"])
        
        if auth_status.get("user_role"):
            table.add_row("User Role", auth_status["user_role"])
        
        # Add JWT status
        jwt_status = "[green]✓ Valid[/green]" if auth_status.get("jwt_valid") else "[red]✗ Invalid/Expired[/red]"
        table.add_row("JWT Status", jwt_status)
        
        if auth_status.get("created_at"):
            table.add_row("Created", auth_status["created_at"][:19])
        
        if auth_status.get("last_used"):
            table.add_row("Last Used", auth_status["last_used"][:19])
        
        table.add_row("Total Profiles", str(auth_status["profiles_count"]))
        
        show_table_with_panel(table, "Current authentication information")
        
    except (AuthenticationError, ConfigurationError) as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("profiles")
def profiles_group() -> None:
    """Profile management commands. Use 'polaris auth profiles --help' for subcommands."""
    # This is a placeholder - in a full implementation, this would be a sub-group
    console.print("[yellow]Use one of: list, create, delete, set-default[/yellow]")


@app.command("profiles-list")  
def list_profiles() -> None:
    """List all authentication profiles."""
    
    try:
        token_manager = TokenManager()
        profiles = token_manager.list_profiles()
        
        if not profiles:
            console.print("[yellow]No profiles found[/yellow]")
            console.print("\n[dim]Use [bold]polaris auth login --api-key YOUR_TOKEN[/bold] to create one[/dim]")
            return
        
        # Create profiles table
        table = Table(title="Authentication Profiles")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("User Email", style="blue")
        table.add_column("Created", style="white")
        table.add_column("Last Used", style="dim")
        table.add_column("Token", style="yellow")
        
        for name, profile in profiles.items():
            status = "[green]✓ Default[/green]" if profile.get("is_default") else "[white]Available[/white]"
            created = profile.get("created_at", "N/A")[:19] if profile.get("created_at") else "N/A"
            last_used = profile.get("last_used", "Never")[:19] if profile.get("last_used") else "Never"
            
            # Show Polaris token (not JWT)
            token = profile.get("polaris_token") or profile.get("api_key", "")  # fallback for old profiles
            token_display = f"{token[:10]}..." if token else "N/A"
            
            # Get user email from JWT user info
            user_info = profile.get("user_info", {})
            user_email = user_info.get("email", "N/A")
            
            table.add_row(name, status, user_email, created, last_used, token_display)
        
        show_table_with_panel(table, f"Found {len(profiles)} profile(s)")
        
    except (AuthenticationError, ConfigurationError) as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("profiles-create")
def create_profile(
    name: str = typer.Argument(..., help="Profile name"),
    api_key: str = typer.Option(..., "--api-key", help="API key for this profile")
) -> None:
    """Create a new authentication profile."""
    
    console.print(f"[cyan]Creating profile '[bold]{name}[/bold]'...[/cyan]")
    show_loading_spinner("Validating token", 1.0)
    
    try:
        token_manager = TokenManager()
        token_manager.add_profile(name, api_key)
        
        show_success_message(f"Successfully created profile '{name}'")
        
    except (AuthenticationError, ConfigurationError) as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("profiles-delete")
def delete_profile(
    name: str = typer.Argument(..., help="Profile name to delete")
) -> None:
    """Delete an authentication profile."""
    
    # Confirm deletion
    confirm = typer.confirm(f"Are you sure you want to delete profile '{name}'?")
    if not confirm:
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    try:
        token_manager = TokenManager()
        token_manager.remove_profile(name)
        
        show_success_message(f"Successfully deleted profile '{name}'")
        
    except (AuthenticationError, ConfigurationError) as e:
        show_error_message(str(e))
        raise typer.Exit(1)


@app.command("profiles-set-default")
def set_default_profile(
    name: str = typer.Argument(..., help="Profile name to set as default")
) -> None:
    """Set the default authentication profile."""
    
    try:
        token_manager = TokenManager()
        token_manager.set_default_profile(name)
        
        show_success_message(f"Set '{name}' as the default profile")
        
    except (AuthenticationError, ConfigurationError) as e:
        show_error_message(str(e))
        raise typer.Exit(1)
