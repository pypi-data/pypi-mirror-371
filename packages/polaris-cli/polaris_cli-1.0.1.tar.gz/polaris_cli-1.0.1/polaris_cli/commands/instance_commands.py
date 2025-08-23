"""
Instance management commands
"""

from typing import List, Optional

import typer
from rich.console import Console

from polaris_cli.auth.token_manager import TokenManager
from polaris_cli.ui.banner import (show_error_message, show_loading_spinner,
                                   show_success_message)
from polaris_cli.ui.tables import create_instance_table, show_table_with_panel
from polaris_cli.utils.exceptions import PolarisError

app = typer.Typer(help="Instance lifecycle management")
console = Console()


@app.command("create-help")
def create_help() -> None:
    """Show detailed help for creating instances."""
    from rich.panel import Panel
    
    help_text = """[bold cyan]🚀 Creating an Instance - Step by Step[/bold cyan]

[bold]Step 1: Find Available Resources[/bold]
List all available resources and copy a Resource ID:
[dim]polaris resources list --available-only[/dim]

Example output:
[dim]Resource ID: comp_001 (Singapore) - GPU: NVIDIA RTX A5000[/dim]

[bold]Step 2: Choose a Template[/bold]  
List available templates and copy a Template ID:
[dim]polaris templates list[/dim]

Example output:
[dim]Template ID: tpl_pytorch_gpu (PyTorch with CUDA)[/dim]

[bold]Step 3: Create Your Instance[/bold]
[green]polaris instances create my-training --resource-id comp_001 --template-id tpl_pytorch_gpu[/green]

[bold]Optional: Add SSH Key[/bold]
First list your SSH keys: [dim]polaris ssh keys list[/dim]
Then use: [dim]--ssh-key key_001[/dim]

[bold]💡 Quick Examples:[/bold]
• Training: [dim]--resource-id comp_001 --template-id tpl_pytorch_gpu[/dim]
• Inference: [dim]--resource-id comp_005 --template-id tpl_fastapi_serve[/dim]  
• Development: [dim]--resource-id comp_003 --template-id tpl_vscode_remote[/dim]"""
    
    console.print(Panel(help_text, border_style="cyan", padding=(1, 2)))


def require_authentication() -> TokenManager:
    """Check if user is authenticated and return TokenManager."""
    token_manager = TokenManager()
    if not token_manager.is_authenticated():
        show_error_message("Authentication required. Use 'polaris auth login --api-key YOUR_TOKEN'")
        raise typer.Exit(1)
    return token_manager


@app.command("list")
def list_instances(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
    region: Optional[str] = typer.Option(None, "--region", help="Filter by region"),
    output: str = typer.Option("table", "--output", help="Output format (table|json|csv)")
) -> None:
    """List your instances."""
    
    token_manager = require_authentication()
    
    console.print("[cyan]Loading instances...[/cyan]")
    show_loading_spinner("Fetching instance data", 1.0)
    
    try:
        # Get authenticated API client and fetch instances
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.list_instances(status=status, region=region)
        
        instances = response.get("instances", [])
        total_count = response.get("total_count", len(instances))
        
        if not instances:
            if output == "json":
                console.print_json(data={"instances": [], "total_count": 0})
                return
            elif output == "csv":
                console.print("id,name,status,region,hourly_price,created_at,duration_days")
                return
            else:
                console.print("[yellow]No instances found[/yellow]")
                console.print("[dim]Create one with: [bold]polaris instances create --help[/bold][/dim]")
                return
        
        # Handle JSON output
        if output == "json":
            console.print_json(data=response)
            return
        
        # Handle CSV output  
        if output == "csv":
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow(["id", "name", "status", "region", "hourly_price", "created_at", "duration_days", "expires_at"])
            
            # Write data rows
            for instance in instances:
                writer.writerow([
                    instance.get("id", ""),
                    instance.get("name", ""),
                    instance.get("status", ""),
                    instance.get("region", ""),
                    instance.get("hourly_price", ""),
                    instance.get("created_at", ""),
                    instance.get("duration_days", ""),
                    instance.get("expires_at", "")
                ])
            
            console.print(output_buffer.getvalue().strip())
            return
        
        # Table output (default)
        table = create_instance_table(instances)
        show_table_with_panel(table, f"Found {len(instances)} instance(s) (Total: {total_count})")
        
    except PolarisError as e:
        show_error_message(f"Failed to fetch instances: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("create")
def create_instance(
    name: str = typer.Argument(..., help="Instance name"),
    resource_id: str = typer.Option(..., "--resource-id", help="Resource ID (get from 'polaris resources list')"),
    template_id: str = typer.Option(..., "--template-id", help="Template ID (get from 'polaris templates list')"),
    ssh_key: Optional[str] = typer.Option(None, "--ssh-key", help="SSH key ID (get from 'polaris ssh keys list')"),
    disk_size: int = typer.Option(100, "--disk-size", help="Disk size in GB"),
    auto_shutdown: int = typer.Option(0, "--auto-shutdown", help="Auto shutdown after N hours (0=disabled)"),
    duration: int = typer.Option(1, "--duration", help="Instance duration in days (1, 7, or 30)")
) -> None:
    """
    Create a new instance.
    
    \b
    📋 STEP-BY-STEP GUIDE:
    
    1. First, find a resource:
       polaris resources list
       (Copy the Resource ID, e.g., '3408d8c8-cfc7-4ec1-896b-76f82a305326')
    
    2. Then, choose a template:
       polaris templates list
       (Copy the Template ID, e.g., 'pytorch-gpu')
    
    3. Finally, create your instance:
       polaris instances create my-training --resource-id 3408d8c8-cfc7-4ec1-896b-76f82a305326 --template-id pytorch-gpu --duration 7
    
    \b
    💡 TIP: You can also list SSH keys with 'polaris ssh keys-list' if you want to specify one.
    """
    
    token_manager = require_authentication()
    
    # Validate duration
    if duration not in [1, 7, 30]:
        show_error_message(f"Invalid duration: {duration}. Duration must be 1, 7, or 30 days.")
        raise typer.Exit(1)
    
    try:
        console.print(f"[cyan]Creating instance '[bold]{name}[/bold]'...[/cyan]")
        console.print(f"[dim]• Resource ID: {resource_id}[/dim]")
        console.print(f"[dim]• Template ID: {template_id}[/dim]")
        console.print(f"[dim]• SSH Key: {ssh_key or 'None (password auth)'}[/dim]")
        console.print(f"[dim]• Disk Size: {disk_size}GB[/dim]")
        console.print(f"[dim]• Duration: {duration} day(s)[/dim]")
        
        show_loading_spinner("Provisioning instance", 2.0)
        
        # Get authenticated API client and create instance
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.create_instance(
            name=name,
            resource_id=resource_id,
            template_id=template_id,
            ssh_key_id=ssh_key,
            disk_size=disk_size,
            auto_shutdown=auto_shutdown,
            duration_days=duration
        )
        
        instance_info = response.get("instance", {})
        instance_id = instance_info.get("id", "unknown")
        
        show_success_message(f"Successfully created instance '{name}' (ID: {instance_id})")
        
        # Show instance details
        if instance_info:
            console.print(f"[dim]• Status: {instance_info.get('status', 'unknown')}[/dim]")
            console.print(f"[dim]• Region: {instance_info.get('region', 'unknown')}[/dim]")
            console.print(f"[dim]• Hourly Price: ${instance_info.get('hourly_price', 0):.2f}[/dim]")
            if instance_info.get('estimated_total_cost'):
                console.print(f"[dim]• Estimated Total Cost: ${instance_info.get('estimated_total_cost', 0):.2f}[/dim]")
            if instance_info.get('expires_at'):
                console.print(f"[dim]• Expires At: {instance_info.get('expires_at')}[/dim]")
        
        console.print(f"\n[dim]Use [bold]polaris instances get {instance_id}[/bold] to view details[/dim]")
        console.print(f"[dim]SSH: [bold]polaris ssh connect {instance_id}[/bold][/dim]")
        
    except PolarisError as e:
        show_error_message(f"Failed to create instance: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("get")
def get_instance(
    instance_id: str = typer.Argument(..., help="Instance ID"),
    output: str = typer.Option("table", "--output", help="Output format (table|json)")
) -> None:
    """Get detailed information about an instance."""
    
    token_manager = require_authentication()
    
    console.print(f"[cyan]Loading instance [bold]{instance_id}[/bold]...[/cyan]")
    show_loading_spinner("Fetching instance details", 1.0)
    
    try:
        # Get authenticated API client and fetch instance details
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.get_instance(instance_id)
        
        instance = response.get("instance", {})
        
        if not instance:
            show_error_message(f"Instance '{instance_id}' not found")
            raise typer.Exit(1)
        
        # Handle JSON output
        if output == "json":
            console.print_json(data=response)
            return
        
        # Display detailed instance info in table format
        from rich.table import Table
        table = Table(title=f"Instance Details - {instance_id}", show_header=False)
        table.add_column("Field", style="bright_cyan", no_wrap=True, width=20)
        table.add_column("Value", style="bright_white", width=50)
        
        # Format key instance fields with better display
        fields_to_show = [
            ("ID", instance.get("id", "")),
            ("Name", instance.get("name", "")),
            ("Status", f"[bright_green]{instance.get('status', '')}[/bright_green]" if instance.get('status') == 'running' else f"[bright_yellow]{instance.get('status', '')}[/bright_yellow]"),
            ("Region", instance.get("region", "")),
            ("Machine Type", instance.get("machine_type", "")),
            ("Image", instance.get("image", "")),
            ("Created At", instance.get("created_at", "")),
            ("Started At", instance.get("started_at", "")),
            ("Expires At", instance.get("expires_at", "")),
            ("Duration (days)", instance.get("duration_days", "")),
            ("Time Remaining", instance.get("time_remaining", "")),
            ("Hourly Price", f"${instance.get('hourly_price', 0):.2f}"),
            ("Total Cost", f"${instance.get('total_cost', 0):.2f}"),
            ("Disk Size", f"{instance.get('disk_size', '')}GB"),
            ("Auto Shutdown", f"{instance.get('auto_shutdown', 0)} hours" if instance.get('auto_shutdown', 0) > 0 else "Disabled"),
            ("SSH Key ID", instance.get("ssh_key_id", "None")),
        ]
        
        # Add resource specs
        if instance.get("cpu_count"):
            fields_to_show.append(("CPU Count", instance.get("cpu_count", "")))
        if instance.get("gpu_count"):
            fields_to_show.append(("GPU Count", instance.get("gpu_count", "")))
        if instance.get("ram"):
            fields_to_show.append(("RAM", instance.get("ram", "")))
        
        # Add network info
        network = instance.get("network", {})
        if network:
            if network.get("public_ip"):
                fields_to_show.append(("Public IP", network.get("public_ip", "")))
            if network.get("private_ip"):
                fields_to_show.append(("Private IP", network.get("private_ip", "")))
            if network.get("ssh_port"):
                fields_to_show.append(("SSH Port", str(network.get("ssh_port", ""))))
        
        # Add resource usage if available
        usage = instance.get("resource_usage", {})
        if usage:
            if usage.get("cpu_usage"):
                fields_to_show.append(("CPU Usage", usage.get("cpu_usage", "")))
            if usage.get("ram_usage"):
                fields_to_show.append(("RAM Usage", usage.get("ram_usage", "")))
            if usage.get("gpu_usage"):
                fields_to_show.append(("GPU Usage", usage.get("gpu_usage", "")))
            if usage.get("disk_usage"):
                fields_to_show.append(("Disk Usage", usage.get("disk_usage", "")))
        
        # Add storage info
        storage = instance.get("storage", {})
        if storage:
            if storage.get("used_gb"):
                fields_to_show.append(("Storage Used", f"{storage.get('used_gb', '')}GB / {storage.get('total_gb', '')}GB"))
            if storage.get("type"):
                fields_to_show.append(("Storage Type", storage.get("type", "")))
        
        # Add labels if present
        labels = instance.get("labels", [])
        if labels:
            fields_to_show.append(("Labels", ", ".join(labels)))
        
        for field_name, field_value in fields_to_show:
            if field_value:  # Only show non-empty values
                table.add_row(field_name, str(field_value))
        
        show_table_with_panel(table)
        
    except PolarisError as e:
        show_error_message(f"Failed to get instance details: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("start")
def start_instance(
    instance_id: str = typer.Argument(..., help="Instance ID to start")
) -> None:
    """Start a stopped instance."""
    
    token_manager = require_authentication()
    
    try:
        console.print(f"[cyan]Starting instance [bold]{instance_id}[/bold]...[/cyan]")
        show_loading_spinner("Starting instance", 2.0)
        
        # Get authenticated API client and start instance
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.start_instance(instance_id)
        
        show_success_message(f"Successfully initiated start for instance '{instance_id}'")
        
        # Show response details if available
        status = response.get("status", "")
        estimated_time = response.get("estimated_start_time", "")
        
        if status:
            console.print(f"[dim]• Status: {status}[/dim]")
        if estimated_time:
            console.print(f"[dim]• Estimated start time: {estimated_time}[/dim]")
        
        console.print(f"[dim]Check status with: [bold]polaris instances get {instance_id}[/bold][/dim]")
        
    except PolarisError as e:
        show_error_message(f"Failed to start instance: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("stop")
def stop_instance(
    instance_id: str = typer.Argument(..., help="Instance ID to stop")
) -> None:
    """Stop a running instance."""
    
    token_manager = require_authentication()
    
    try:
        console.print(f"[cyan]Stopping instance [bold]{instance_id}[/bold]...[/cyan]")
        show_loading_spinner("Stopping instance", 1.5)
        
        # Get authenticated API client and stop instance
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.stop_instance(instance_id)
        
        show_success_message(f"Successfully initiated stop for instance '{instance_id}'")
        
        # Show response details if available
        status = response.get("status", "")
        estimated_time = response.get("estimated_stop_time", "")
        
        if status:
            console.print(f"[dim]• Status: {status}[/dim]")
        if estimated_time:
            console.print(f"[dim]• Estimated stop time: {estimated_time}[/dim]")
        
        console.print(f"[dim]Check status with: [bold]polaris instances get {instance_id}[/bold][/dim]")
        
    except PolarisError as e:
        show_error_message(f"Failed to stop instance: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("terminate")
def terminate_instance(
    instance_id: str = typer.Argument(..., help="Instance ID to terminate"),
    force: bool = typer.Option(False, "--force", help="Force termination without confirmation")
) -> None:
    """Terminate an instance (irreversible)."""
    
    token_manager = require_authentication()
    
    if not force:
        confirm = typer.confirm(f"Are you sure you want to terminate instance '{instance_id}'? This action cannot be undone.")
        if not confirm:
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    try:
        console.print(f"[cyan]Terminating instance [bold]{instance_id}[/bold]...[/cyan]")
        show_loading_spinner("Terminating instance", 1.0)
        
        # Get authenticated API client and terminate instance
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.terminate_instance(instance_id)
        
        show_success_message(f"Successfully terminated instance '{instance_id}'")
        
        # Show response details if available
        final_cost = response.get("final_cost", "")
        uptime = response.get("total_uptime", "")
        
        if final_cost:
            console.print(f"[dim]• Final cost: ${final_cost}[/dim]")
        if uptime:
            console.print(f"[dim]• Total uptime: {uptime}[/dim]")
        
    except PolarisError as e:
        show_error_message(f"Failed to terminate instance: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("ssh")
def ssh_to_instance(
    instance_id: str = typer.Argument(..., help="Instance ID to connect to"),
    user: str = typer.Option("root", "--user", help="SSH username")
) -> None:
    """SSH into an instance."""
    
    require_authentication()
    
    console.print(f"[cyan]Connecting to instance [bold]{instance_id}[/bold] as [bold]{user}[/bold]...[/cyan]")
    console.print("[dim]SSH connection would be established here[/dim]")
    console.print(f"[green]ssh {user}@{instance_id}.polaris.cloud[/green]")
    console.print("[yellow]Note: Direct SSH connection is not yet implemented[/yellow]")


@app.command("logs")
def get_instance_logs(
    instance_id: str = typer.Argument(..., help="Instance ID"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow logs in real-time"),
    tail: int = typer.Option(100, "--tail", help="Number of lines to show"),
    since: Optional[str] = typer.Option(None, "--since", help="Show logs since timestamp (ISO format)")
) -> None:
    """Get logs from an instance."""
    
    token_manager = require_authentication()
    
    try:
        console.print(f"[cyan]Fetching logs for instance [bold]{instance_id}[/bold]...[/cyan]")
        show_loading_spinner("Loading logs", 1.0)
        
        # Get authenticated API client and fetch logs
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.get_instance_logs(instance_id, tail=tail, follow=follow, since=since)
        
        logs = response.get("logs", [])
        total_lines = response.get("total_lines", len(logs))
        has_more = response.get("has_more", False)
        
        if not logs:
            console.print("[yellow]No logs found for this instance[/yellow]")
            return
        
        console.print(f"\n[dim]Showing last {len(logs)} lines (Total: {total_lines}){'...' if has_more else ''}[/dim]\n")
        
        for log_entry in logs:
            timestamp = log_entry.get("timestamp", "")
            level = log_entry.get("level", "INFO")
            message = log_entry.get("message", "")
            source = log_entry.get("source", "")
            
            # Format timestamp (show just time if from today)
            display_time = timestamp[:19] if timestamp else ""
            
            # Color code log levels
            if level == "ERROR":
                level_colored = f"[bright_red]{level}[/bright_red]"
            elif level == "WARN" or level == "WARNING":
                level_colored = f"[bright_yellow]{level}[/bright_yellow]"
            elif level == "INFO":
                level_colored = f"[bright_blue]{level}[/bright_blue]"
            else:
                level_colored = f"[dim]{level}[/dim]"
            
            # Format log line
            source_text = f"[{source}]" if source else ""
            log_line = f"{display_time} {level_colored} {source_text} {message}"
            console.print(log_line)
        
        if follow:
            console.print(f"\n[dim]Following logs... (Press Ctrl+C to exit)[/dim]")
            console.print("[yellow]Note: Real-time log following is not yet implemented[/yellow]")
        
    except PolarisError as e:
        show_error_message(f"Failed to get instance logs: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)


@app.command("exec")
def execute_command(
    instance_id: str = typer.Argument(..., help="Instance ID"),
    command: str = typer.Argument(..., help="Command to execute"),
    timeout: int = typer.Option(30, "--timeout", help="Command timeout in seconds"),
    user: str = typer.Option("root", "--user", help="User to run command as"),
    workdir: Optional[str] = typer.Option(None, "--workdir", help="Working directory")
) -> None:
    """Execute a command on an instance."""
    
    token_manager = require_authentication()
    
    try:
        console.print(f"[cyan]Executing command on instance [bold]{instance_id}[/bold]...[/cyan]")
        console.print(f"[dim]Command: {command}[/dim]")
        console.print(f"[dim]User: {user}[/dim]")
        if workdir:
            console.print(f"[dim]Working directory: {workdir}[/dim]")
        console.print(f"[dim]Timeout: {timeout}s[/dim]\n")
        
        show_loading_spinner("Executing command", 1.0)
        
        # Get authenticated API client and execute command
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.execute_command(
            instance_id=instance_id,
            command=command,
            timeout=timeout,
            user=user,
            working_dir=workdir
        )
        
        exit_code = response.get("exit_code", -1)
        stdout = response.get("stdout", "")
        stderr = response.get("stderr", "")
        execution_time = response.get("execution_time", 0)
        
        # Show execution results
        if exit_code == 0:
            console.print("[green]✓ Command executed successfully[/green]")
        else:
            console.print(f"[red]✗ Command failed with exit code {exit_code}[/red]")
        
        console.print(f"[dim]Execution time: {execution_time}s[/dim]\n")
        
        # Show stdout if present
        if stdout:
            console.print("[bright_white]Output:[/bright_white]")
            console.print(stdout)
        
        # Show stderr if present
        if stderr:
            console.print("\n[bright_red]Error output:[/bright_red]")
            console.print(stderr)
        
        if not stdout and not stderr:
            console.print("[dim]No output from command[/dim]")
        
    except PolarisError as e:
        show_error_message(f"Failed to execute command: {e}")
        raise typer.Exit(1)
    except Exception as e:
        show_error_message(f"Unexpected error: {e}")
        raise typer.Exit(1)
