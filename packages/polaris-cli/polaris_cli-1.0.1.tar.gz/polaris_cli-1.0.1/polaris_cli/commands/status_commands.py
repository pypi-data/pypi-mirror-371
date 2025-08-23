"""
System status and monitoring commands
"""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from polaris_cli.commands.instance_commands import require_authentication
from polaris_cli.ui.banner import show_info_box, show_loading_spinner

app = typer.Typer(help="System status and monitoring")
console = Console()


@app.command("overview")
def status_overview() -> None:
    """Show system status overview."""
    
    require_authentication()
    
    console.print("[cyan]Loading system overview...[/cyan]")
    show_loading_spinner("Collecting status data", 1.5)
    
    # Mock status data
    status_info = """
[bold]System Status:[/bold] [green]All Systems Operational[/green]

[bold]Resources:[/bold]
• Instances: 4 (3 running, 1 stopped)
• Clusters: 2 (running)
• Total Cost: $127.50/hour

[bold]Recent Activity:[/bold]
• Instance 'ml-training-job' started 2h ago
• Cluster 'inference-cluster' scaled to 8 nodes
• New template 'pytorch-training' created

[bold]Alerts:[/bold]
• No active alerts
    """.strip()
    
    panel = Panel(
        status_info,
        title="[bold cyan]Polaris Status Overview[/bold cyan]",
        border_style="cyan"
    )
    
    console.print(panel)


@app.command("instances")
def instance_status(
    unhealthy_only: bool = typer.Option(False, "--unhealthy-only", help="Show only unhealthy instances")
) -> None:
    """Show instance health status."""
    
    require_authentication()
    
    console.print("[cyan]Checking instance health...[/cyan]")
    show_loading_spinner("Health check in progress", 1.0)
    
    health_info = """
[bold]Instance Health Status:[/bold]

[green]✓[/green] inst_001 - ml-training-job (Healthy)
[green]✓[/green] inst_002 - inference-server (Healthy)  
[yellow]⚠[/yellow] inst_003 - data-processing (Stopped)
[green]✓[/green] inst_004 - dev-environment (Healthy)

[dim]4 total instances, 3 healthy, 1 stopped[/dim]
    """.strip()
    
    show_info_box("Instance Health", health_info)


@app.command("alerts")
def show_alerts(
    active_only: bool = typer.Option(True, "--active-only", help="Show only active alerts")
) -> None:
    """Show system alerts."""
    
    require_authentication()
    
    console.print("[cyan]Loading alerts...[/cyan]")
    
    if active_only:
        console.print("[green]No active alerts[/green]")
        console.print("\n[dim]Your system is operating normally[/dim]")
    else:
        alerts_info = """
[bold]Recent Alerts (Last 24h):[/bold]

[green]Resolved[/green] - High CPU usage on inst_002 (2h ago)
[green]Resolved[/green] - Disk space low on inst_001 (6h ago)
[green]Resolved[/green] - Network latency spike in us-west-1 (8h ago)

[dim]All alerts have been resolved[/dim]
        """.strip()
        
        show_info_box("System Alerts", alerts_info)
