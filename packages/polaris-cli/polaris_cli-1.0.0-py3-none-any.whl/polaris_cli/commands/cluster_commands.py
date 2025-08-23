"""
Cluster management commands
"""

from typing import Optional

import typer
from rich.console import Console

from polaris_cli.commands.instance_commands import require_authentication
from polaris_cli.data.dummy_data import get_sample_clusters
from polaris_cli.ui.banner import show_loading_spinner, show_success_message
from polaris_cli.ui.tables import show_table_with_panel

app = typer.Typer(help="Cluster operations")
console = Console()


@app.command("list")
def list_clusters() -> None:
    """List your clusters."""
    
    require_authentication()
    
    console.print("[cyan]Loading clusters...[/cyan]")
    show_loading_spinner("Fetching cluster data", 1.0)
    
    clusters = get_sample_clusters()
    
    from rich.table import Table
    table = Table(title="Clusters")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")
    table.add_column("Nodes", style="blue", justify="center")
    table.add_column("Machine Type", style="yellow")
    table.add_column("Region", style="magenta")
    table.add_column("Cost/hr", style="bright_green", justify="right")
    
    for cluster in clusters:
        table.add_row(
            cluster["id"],
            cluster["name"],
            cluster["status"],
            str(cluster["node_count"]),
            cluster["machine_type"],
            cluster["region"],
            f"${cluster['price_per_hour']:.2f}"
        )
    
    show_table_with_panel(table, f"Found {len(clusters)} cluster(s)")


@app.command("create")
def create_cluster(
    name: str = typer.Argument(..., help="Cluster name"),
    node_count: int = typer.Option(3, "--node-count", help="Initial number of nodes"),
    machine_type: str = typer.Option("gpu-nvidia-a100-80gb", "--machine-type", help="Machine type for nodes"),
    auto_scale: bool = typer.Option(False, "--auto-scale", help="Enable auto-scaling"),
    min_nodes: int = typer.Option(1, "--min", help="Minimum nodes for auto-scaling"),
    max_nodes: int = typer.Option(10, "--max", help="Maximum nodes for auto-scaling")
) -> None:
    """Create a new cluster."""
    
    require_authentication()
    
    console.print(f"[cyan]Creating cluster '[bold]{name}[/bold]' with {node_count} nodes...[/cyan]")
    show_loading_spinner("Provisioning cluster", 4.0)
    
    cluster_id = f"cluster_{name.lower().replace('-', '_')}"
    
    show_success_message(f"Successfully created cluster '{name}' (ID: {cluster_id})")
    console.print(f"\n[dim]Use [bold]polaris clusters get {cluster_id}[/bold] to view details[/dim]")


@app.command("scale")
def scale_cluster(
    cluster_id: str = typer.Argument(..., help="Cluster ID"),
    nodes: int = typer.Option(..., "--nodes", help="Target number of nodes")
) -> None:
    """Scale a cluster to the specified number of nodes."""
    
    require_authentication()
    
    console.print(f"[cyan]Scaling cluster [bold]{cluster_id}[/bold] to {nodes} nodes...[/cyan]")
    show_loading_spinner("Scaling cluster", 3.0)
    
    show_success_message(f"Successfully scaled cluster '{cluster_id}' to {nodes} nodes")


@app.command("delete")
def delete_cluster(
    cluster_id: str = typer.Argument(..., help="Cluster ID to delete"),
    force: bool = typer.Option(False, "--force", help="Force deletion without confirmation")
) -> None:
    """Delete a cluster."""
    
    require_authentication()
    
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete cluster '{cluster_id}'?")
        if not confirm:
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    console.print(f"[cyan]Deleting cluster [bold]{cluster_id}[/bold]...[/cyan]")
    show_loading_spinner("Deleting cluster", 2.0)
    
    show_success_message(f"Successfully deleted cluster '{cluster_id}'")
