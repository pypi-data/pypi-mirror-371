"""
Billing and usage management commands
"""

from typing import Optional

import typer
from rich.console import Console

from polaris_cli.commands.instance_commands import require_authentication
from polaris_cli.data.dummy_data import get_sample_billing_data
from polaris_cli.ui.banner import show_info_box, show_loading_spinner
from polaris_cli.ui.tables import create_billing_table, show_table_with_panel

app = typer.Typer(help="Billing and usage management")
console = Console()


@app.command("overview")
def billing_overview(
    period: str = typer.Option("current", "--period", help="Billing period (current|30d|90d)")
) -> None:
    """Show billing overview."""
    
    require_authentication()
    
    console.print(f"[cyan]Loading billing overview for [bold]{period}[/bold]...[/cyan]")
    show_loading_spinner("Calculating costs", 1.5)
    
    # Mock billing overview
    overview_info = f"""
[bold]Billing Overview - {period.upper()}[/bold]

[bold]Current Usage:[/bold]
• Total Cost: $1,933.58
• Compute Hours: 2,364.5 hours
• Active Instances: 4
• Storage: 1.2 TB

[bold]Cost Breakdown:[/bold]
• GPU Instances: $1,774.25 (92%)
• CPU Instances: $85.33 (4%)
• Storage: $74.00 (4%)

[bold]Trends:[/bold]
• 15% increase from last period
• Peak usage: Jan 10-15
• Projected monthly: $2,150.00
    """.strip()
    
    show_info_box("Billing Overview", overview_info)


@app.command("usage")
def usage_details(
    instance: Optional[str] = typer.Option(None, "--instance", help="Show usage for specific instance"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="End date (YYYY-MM-DD)")
) -> None:
    """Show detailed usage information."""
    
    require_authentication()
    
    console.print("[cyan]Loading usage details...[/cyan]")
    show_loading_spinner("Analyzing usage patterns", 1.0)
    
    billing_data = get_sample_billing_data()
    
    # Apply filters
    if instance:
        billing_data = [b for b in billing_data if b.get("resource") == instance]
    
    if not billing_data:
        console.print("[yellow]No usage data found for the specified criteria[/yellow]")
        return
    
    table = create_billing_table(billing_data)
    show_table_with_panel(table, f"Usage for {len(billing_data)} resource(s)")


@app.command("costs")
def cost_breakdown(
    breakdown: bool = typer.Option(True, "--breakdown", help="Show detailed cost breakdown"),
    period: str = typer.Option("current", "--period", help="Time period")
) -> None:
    """Show cost breakdown and analysis."""
    
    require_authentication()
    
    console.print("[cyan]Analyzing costs...[/cyan]")
    show_loading_spinner("Computing cost breakdown", 1.0)
    
    if breakdown:
        cost_info = """
[bold]Detailed Cost Breakdown:[/bold]

[bold]By Resource Type:[/bold]
• GPU Instances: $1,774.25 (91.7%)
• CPU Instances: $85.33 (4.4%)
• Storage: $74.00 (3.9%)

[bold]By Instance:[/bold]
• ml-training-cluster: $1,411.20 (72.9%)
• inference-server: $133.20 (6.9%)
• ml-training-job: $442.25 (22.9%)
• dev-environment: $45.33 (2.3%)

[bold]Top Cost Drivers:[/bold]
1. H100 GPU usage (cluster_001)
2. A100 GPU hours (inst_001)
3. Network data transfer
        """.strip()
        
        show_info_box("Cost Analysis", cost_info)
    else:
        console.print(f"[bold]Total costs for {period}:[/bold] [green]$1,933.58[/green]")


@app.command("invoices")
def manage_invoices() -> None:
    """Invoice management. Use subcommands like 'invoices-list'."""
    console.print("[cyan]Invoice commands:[/cyan]")
    console.print("  • polaris billing invoices-list")
    console.print("  • polaris billing invoices-get")
    console.print("  • polaris billing invoices-download")


@app.command("invoices-list") 
def list_invoices() -> None:
    """List billing invoices."""
    
    require_authentication()
    
    console.print("[cyan]Loading invoices...[/cyan]")
    show_loading_spinner("Fetching invoice data", 1.0)
    
    from rich.table import Table
    table = Table(title="Invoices")
    table.add_column("Invoice ID", style="cyan", no_wrap=True)
    table.add_column("Period", style="white")
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Status", style="yellow")
    table.add_column("Due Date", style="dim")
    
    # Mock invoice data
    invoices = [
        ("inv_20240131_001", "2024-01", "$442.25", "Paid", "2024-02-15"),
        ("inv_20240131_002", "2024-01", "$1,332.00", "Paid", "2024-02-15"),
        ("inv_20240228_001", "2024-02", "$45.33", "Pending", "2024-03-15"),
    ]
    
    for invoice in invoices:
        table.add_row(*invoice)
    
    show_table_with_panel(table, f"Found {len(invoices)} invoice(s)")


@app.command("limits")
def billing_limits() -> None:
    """Show and manage billing limits."""
    
    require_authentication()
    
    console.print("[cyan]Loading billing limits...[/cyan]")
    
    limits_info = """
[bold]Current Billing Limits:[/bold]

[bold]Spending Limits:[/bold]
• Daily Limit: $500.00 (Current: $127.50)
• Monthly Limit: $5,000.00 (Current: $1,933.58)
• Alert Threshold: $100.00 per day

[bold]Resource Limits:[/bold]
• Max Instances: 50 (Current: 4)
• Max GPU Hours: 10,000/month (Current: 1,844)
• Max Storage: 10 TB (Current: 1.2 TB)

[bold]Status:[/bold] [green]All limits within range[/green]
    """.strip()
    
    show_info_box("Billing Limits", limits_info)
