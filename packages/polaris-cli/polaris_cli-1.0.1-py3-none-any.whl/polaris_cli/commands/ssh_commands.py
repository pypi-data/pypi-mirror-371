"""
SSH access and key management commands
"""

from typing import Optional

import typer
from rich.console import Console

from polaris_cli.auth.token_manager import TokenManager
from polaris_cli.ui.banner import (show_error_message, show_loading_spinner,
                                   show_success_message)
from polaris_cli.ui.tables import show_table_with_panel
from polaris_cli.utils.exceptions import PolarisError

app = typer.Typer(help="SSH access and key management")
console = Console()


def require_authentication() -> TokenManager:
    """Check if user is authenticated and return TokenManager."""
    token_manager = TokenManager()
    if not token_manager.is_authenticated():
        show_error_message("Authentication required. Use 'polaris auth login --api-key YOUR_TOKEN'")
        raise typer.Exit(1)
    return token_manager


@app.command("keys")
def ssh_keys() -> None:
    """SSH key management. Use subcommands like 'keys-list'."""
    console.print("[cyan]SSH key commands:[/cyan]")
    console.print("  • polaris ssh keys-list")
    console.print("  • polaris ssh keys-add")
    console.print("  • polaris ssh keys-delete")


@app.command("keys-list")
def list_ssh_keys(
    output: str = typer.Option("table", "--output", help="Output format (table|json|csv)")
) -> None:
    """List your SSH keys."""
    
    token_manager = require_authentication()
    
    console.print("[cyan]Loading SSH keys...[/cyan]")
    show_loading_spinner("Fetching SSH keys", 1.0)
    
    try:
        # Get authenticated API client
        api_client = token_manager.get_authenticated_api_client()
        
        # Fetch SSH keys from API
        response = api_client.list_ssh_keys()
        ssh_keys = response.get("keys", [])
        
        if not ssh_keys:
            if output == "json":
                console.print_json(data={"keys": []})
                return
            elif output == "csv":
                console.print("id,name,key_type,bits,fingerprint,is_default,last_used")
                return
            else:
                console.print("[yellow]No SSH keys found[/yellow]")
                console.print("[dim]Add a key with: [bold]polaris ssh keys-add <name> --key-file <path>[/bold][/dim]")
                return
        
        # Handle JSON output
        if output == "json":
            console.print_json(data={"keys": ssh_keys})
            return
        
        # Handle CSV output  
        if output == "csv":
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow(["id", "name", "key_type", "bits", "fingerprint", "is_default", "last_used"])
            
            # Write data rows
            for key in ssh_keys:
                writer.writerow([
                    key.get("id", ""),
                    key.get("name", ""),
                    key.get("key_type", ""),
                    key.get("bits", ""),
                    key.get("fingerprint", ""),
                    key.get("is_default", False),
                    key.get("last_used", "")
                ])
            
            console.print(output_buffer.getvalue().strip())
            return
        
        from rich.table import Table
        table = Table(title="SSH Keys")
        table.add_column("ID", style="bright_cyan", no_wrap=True, width=22)
        table.add_column("Name", style="bright_white", no_wrap=False, width=16)
        table.add_column("Type", style="bright_blue", width=12)
        table.add_column("Bits", style="bright_yellow", justify="center", width=6)
        table.add_column("Fingerprint", style="dim", no_wrap=False, width=16)
        table.add_column("Status", style="bright_green", width=9)
        table.add_column("Last Used", style="dim", width=11)
        
        for key in ssh_keys:
            status = "[bright_green]Default[/bright_green]" if key.get("is_default") else "[bright_white]Active[/bright_white]"
            last_used = key.get("last_used", "Never")
            if last_used and last_used != "Never":
                # Format ISO date to just show date part
                try:
                    last_used = last_used[:10]
                except:
                    pass
            
            # Format name with line breaks if long
            name = key.get("name", "")
            if len(name) > 14:
                # Break long names at reasonable points
                if "-" in name:
                    parts = name.split("-")
                    if len(parts) >= 2:
                        # Find the best break point that doesn't exceed ~14 chars per line
                        for i in range(1, len(parts)):
                            first_part = "-".join(parts[:i])
                            if len(first_part) >= 8:  # Try to get at least 8 chars in first line
                                name_display = first_part + "-\n" + "-".join(parts[i:])
                                break
                        else:
                            # Fallback: split in middle
                            mid_point = len(parts) // 2
                            name_display = "-".join(parts[:mid_point]) + "-\n" + "-".join(parts[mid_point:])
                    else:
                        name_display = name[:14] + "\n" + name[14:]
                elif "_" in name:
                    parts = name.split("_")
                    if len(parts) >= 2:
                        # Similar logic for underscore
                        for i in range(1, len(parts)):
                            first_part = "_".join(parts[:i])
                            if len(first_part) >= 8:
                                name_display = first_part + "_\n" + "_".join(parts[i:])
                                break
                        else:
                            mid_point = len(parts) // 2
                            name_display = "_".join(parts[:mid_point]) + "_\n" + "_".join(parts[mid_point:])
                    else:
                        name_display = name[:14] + "\n" + name[14:]
                else:
                    # No natural break point, split at midpoint
                    name_display = name[:14] + "\n" + name[14:]
            else:
                name_display = name
            
            # Format fingerprint with line breaks if long
            fingerprint = key.get("fingerprint", "")
            if len(fingerprint) > 14:
                # For SHA256 fingerprints, break after the prefix and show limited chars
                if fingerprint.startswith("SHA256:"):
                    # Show first 8 chars of the hash
                    hash_part = fingerprint[7:]
                    fingerprint_display = "SHA256:\n" + hash_part[:8] + "..."
                else:
                    # Break at midpoint for other formats but limit length
                    fingerprint_display = fingerprint[:8] + "\n" + fingerprint[8:16] + "..."
            else:
                fingerprint_display = fingerprint
            
            table.add_row(
                key.get("id", ""),
                name_display,
                key.get("key_type", ""),
                str(key.get("bits", "")),
                fingerprint_display,
                status,
                last_used or "Never"
            )
        
        show_table_with_panel(table, f"Found {len(ssh_keys)} SSH key(s)")
        
    except PolarisError as e:
        show_error_message(f"Failed to fetch SSH keys: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("keys-add")
def add_ssh_key(
    name: str = typer.Argument(..., help="Key name"),
    key_file: str = typer.Option(..., "--key-file", help="Path to public key file")
) -> None:
    """Add a new SSH key."""
    
    token_manager = require_authentication()
    
    try:
        # Read the public key file
        import os
        if not os.path.exists(key_file):
            show_error_message(f"Key file not found: {key_file}")
            raise typer.Exit(1)
        
        with open(key_file, 'r') as f:
            public_key = f.read().strip()
        
        if not public_key:
            show_error_message("Key file is empty")
            raise typer.Exit(1)
        
        # Basic validation - check if it looks like a public key
        if not (public_key.startswith('ssh-rsa') or public_key.startswith('ssh-ed25519') or public_key.startswith('ssh-dss')):
            show_error_message("Invalid public key format. Key should start with ssh-rsa, ssh-ed25519, or ssh-dss")
            raise typer.Exit(1)
        
        console.print(f"[cyan]Adding SSH key '[bold]{name}[/bold]'...[/cyan]")
        show_loading_spinner("Uploading key", 1.5)
        
        # Get authenticated API client and add the key
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.add_ssh_key(name, public_key)
        
        key_info = response.get("key", {})
        key_id = key_info.get("id", "unknown")
        
        show_success_message(f"Successfully added SSH key '{name}' (ID: {key_id})")
        
        # Show key details
        if key_info:
            console.print(f"[dim]• Type: {key_info.get('key_type', 'unknown')}[/dim]")
            console.print(f"[dim]• Bits: {key_info.get('bits', 'unknown')}[/dim]")
            console.print(f"[dim]• Fingerprint: {key_info.get('fingerprint', 'unknown')[:50]}...[/dim]")
        
    except FileNotFoundError:
        show_error_message(f"Key file not found: {key_file}")
        raise typer.Exit(1)
    except PermissionError:
        show_error_message(f"Permission denied reading key file: {key_file}")
        raise typer.Exit(1)
    except PolarisError as e:
        show_error_message(f"Failed to add SSH key: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("keys-delete")
def delete_ssh_key(
    key_id: str = typer.Argument(..., help="SSH key ID to delete")
) -> None:
    """Delete an SSH key."""
    
    token_manager = require_authentication()
    
    try:
        confirm = typer.confirm(f"Are you sure you want to delete SSH key '{key_id}'?")
        if not confirm:
            console.print("[yellow]Operation cancelled[/yellow]")
            return
        
        console.print(f"[cyan]Deleting SSH key [bold]{key_id}[/bold]...[/cyan]")
        show_loading_spinner("Deleting key", 1.0)
        
        # Get authenticated API client and delete the key
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.delete_ssh_key(key_id)
        
        show_success_message(f"Successfully deleted SSH key '{key_id}'")
        
        # Show additional info if available
        message = response.get("message", "")
        if message:
            console.print(f"[dim]{message}[/dim]")
            
    except PolarisError as e:
        show_error_message(f"Failed to delete SSH key: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("connect")
def connect_to_instance(
    instance_id: str = typer.Argument(..., help="Instance ID to connect to"),
    user: str = typer.Option("root", "--user", help="SSH username"),
    port: int = typer.Option(22, "--port", help="SSH port")
) -> None:
    """Connect to an instance via SSH."""
    
    require_authentication()
    
    console.print(f"[cyan]Connecting to [bold]{instance_id}[/bold] as [bold]{user}[/bold]...[/cyan]")
    console.print(f"[green]ssh -p {port} {user}@{instance_id}.polaris.cloud[/green]")
    console.print("[dim]SSH connection would be established here[/dim]")
    console.print("[yellow]Note: SSH connection endpoints are not yet implemented in the API[/yellow]")


@app.command("tunnel")
def create_tunnel(
    instance_id: str = typer.Argument(..., help="Instance ID"),
    local_port: int = typer.Option(..., "--local-port", help="Local port"),
    remote_port: int = typer.Option(..., "--remote-port", help="Remote port")
) -> None:
    """Create an SSH tunnel to an instance."""
    
    require_authentication()
    
    console.print(f"[cyan]Creating tunnel to [bold]{instance_id}[/bold]...[/cyan]")
    console.print(f"[dim]Local port {local_port} -> Remote port {remote_port}[/dim]")
    
    tunnel_cmd = f"ssh -L {local_port}:localhost:{remote_port} root@{instance_id}.polaris.cloud"
    console.print(f"[green]{tunnel_cmd}[/green]")
    console.print("[dim]SSH tunnel would be established here[/dim]")
    console.print("[yellow]Note: SSH tunnel endpoints are not yet implemented in the API[/yellow]")
