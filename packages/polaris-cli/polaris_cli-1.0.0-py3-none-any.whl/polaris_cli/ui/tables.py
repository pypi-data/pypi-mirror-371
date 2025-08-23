"""
Beautiful table formatting for CLI output
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def create_resource_table(resources: List[Dict[str, Any]], title: str = "Resources") -> Table:
    """Create a beautifully formatted table for resource listings."""
    
    table = Table(
        title=f"[bright_white]{title}[/bright_white]",
        show_header=True,
        header_style="bright_white",
        border_style="bright_cyan",
        title_style="bright_white",
        show_lines=True,  # Add horizontal lines between rows
        width=120,  # Smaller but readable
        padding=(0, 0),  # Even smaller padding
    )
    
    # Updated columns with bright, vibrant styling
    if resources and len(resources) > 0:
        table.add_column("Resource ID", style="bright_cyan", width=16, no_wrap=False)
        table.add_column("Resource", style="bright_red", width=20)
        table.add_column("GPU Specifications", style="bright_green", width=20)
        table.add_column("CPU Details", style="bright_blue", width=30)
        table.add_column("Price/hr", style="bright_green", justify="right", width=10)
        table.add_column("Status", style="bright_white", width=10)
        
        # Populate rows
        for resource in resources:
            # Get network info from real API structure
            network_info = resource.get("network_info", {})
            city = network_info.get("city", "Unknown")
            country = network_info.get("country", "Unknown")
            region = network_info.get("region", "Unknown")
            
            # Get GPU info
            gpu_specs = resource.get("gpu_specs", {})
            gpu_model = gpu_specs.get("model_name", "no discrete GPU detected")
            gpu_memory = gpu_specs.get("memory", "N/A")
            gpu_count = resource.get("gpu_count", 0)
            
            # Get CPU info from real API structure
            cpu_specs = resource.get("cpu_specs", {})
            cpu_model = cpu_specs.get("model_name", "Unknown")
            cpu_cores = cpu_specs.get("cores", resource.get("cpu_count", 0))
            cpu_threads = cpu_specs.get("threads", 0)
            cpu_clock = cpu_specs.get("clock_speed", "Unknown")
            
            # Resource column - Type, Region, Model, Count
            resource_type = resource.get("resource_type", "Unknown")
            if gpu_count > 0:
                # GPU resource
                region_info = f"{region}, {country}"
                model_info = gpu_model if gpu_model != "no discrete GPU detected" else cpu_model
                count_info = f"{gpu_count}x"
            else:
                # CPU-only resource
                region_info = f"{region}, {country}"
                model_info = cpu_model
                count_info = f"{cpu_cores}x"
            
            resource_config = f"Type: {resource_type}\nRegion: {region_info}\nModel: {model_info}\nCount: {count_info}"
            
            # GPU Specifications - VRAM and System RAM from real API structure
            system_ram = resource.get('ram', '0GB')  # Already includes GB suffix
            storage_info = resource.get('storage', {})
            if isinstance(storage_info, dict):
                storage_gb = storage_info.get('total_gb', 0)
                storage_type = storage_info.get('type', 'Unknown')
                storage_display = f"{storage_gb}GB"
            else:
                storage_display = str(storage_info)
            
            if gpu_count > 0:
                gpu_specs_display = f"VRAM: {gpu_memory}\n"
                gpu_specs_display += f"System RAM: {system_ram}\n"
                gpu_specs_display += f"Storage: {storage_display}"
            else:
                # CPU-only resource - show system specs here instead
                gpu_specs_display = f"No GPU\n"
                gpu_specs_display += f"System RAM: {system_ram}\n"
                gpu_specs_display += f"Storage: {storage_display}"
            
            # CPU Details - detailed specifications from real API
            cpu_architecture = cpu_specs.get("architecture", "Unknown")
            
            cpu_details = f"Model: {cpu_model}\n"
            cpu_details += f"Cores: {cpu_cores} cores\n"
            cpu_details += f"Threads: {cpu_threads} threads\n"
            cpu_details += f"Clock: {cpu_clock}\n"
            cpu_details += f"Cache: {cpu_architecture}"  # Using architecture as cache isn't in API
            
            # Get Resource ID from real API structure (format UUID for better display)
            full_resource_id = resource.get("resource_id", "N/A")
            if len(full_resource_id) == 36 and full_resource_id != "N/A":  # Standard UUID length
                # Break UUID into 2 lines for better display
                resource_id = f"{full_resource_id[:18]}\n{full_resource_id[18:]}"
            else:
                resource_id = full_resource_id
            
            # Status with availability from real API structure (simple display)
            deployment_status = resource.get("deployment_status", "unknown")
            
            if deployment_status == "inactive":
                status = "[bright_green]Available[/bright_green]"
            elif deployment_status == "active":
                status = "[bright_red]In Use[/bright_red]"
            else:
                status = f"[bright_yellow]{deployment_status.title()}[/bright_yellow]"
            
            row = [
                resource_id,
                resource_config,
                gpu_specs_display,
                cpu_details,
                format_price(resource.get("hourly_price", 0)),  # Real API uses hourly_price
                status,
            ]
            
            table.add_row(*row)
    
    return table


def create_instance_table(instances: List[Dict[str, Any]]) -> Table:
    """Create a table for instance listings."""
    
    table = Table(
        title="[bold cyan]Instances[/bold cyan]",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="cyan",
        title_style="bold cyan",
        show_lines=True,
    )
    
    table.add_column("ID", style="bright_white", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Status", style="green")
    table.add_column("Machine Type", style="blue")
    table.add_column("Region", style="yellow")
    table.add_column("Uptime", style="cyan")
    table.add_column("Cost", style="bright_green", justify="right")
    
    for instance in instances:
        uptime = format_uptime(instance.get("created_at"))
        cost = calculate_cost(instance.get("created_at"), instance.get("price_per_hour", 0))
        
        table.add_row(
            str(instance.get("id", "N/A")),
            instance.get("name", "N/A"),
            format_status(instance.get("status", "unknown")),
            instance.get("machine_type", "N/A"),
            instance.get("region", "N/A"),
            uptime,
            f"${cost:.2f}",
        )
    
    return table


def create_billing_table(billing_data: List[Dict[str, Any]]) -> Table:
    """Create a table for billing information."""
    
    table = Table(
        title="[bold cyan]Billing Summary[/bold cyan]",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="cyan",
        title_style="bold cyan",
        show_lines=True,
    )
    
    table.add_column("Period", style="white")
    table.add_column("Resource", style="blue")
    table.add_column("Usage", style="cyan", justify="right")
    table.add_column("Cost", style="bright_green", justify="right")
    table.add_column("Status", style="green")
    
    for item in billing_data:
        table.add_row(
            item.get("period", "N/A"),
            item.get("resource", "N/A"),
            item.get("usage", "N/A"),
            format_price(item.get("cost", 0)),
            format_status(item.get("status", "unknown")),
        )
    
    return table


def create_comparison_table(items: List[Dict[str, Any]], title: str = "Comparison") -> Table:
    """Create a comparison table for resources."""
    
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style="bold bright_cyan",
        border_style="cyan",
        title_style="bold cyan",
        show_lines=True,
    )
    
    if not items:
        return table
    
    # Get all possible attributes
    all_attrs = set()
    for item in items:
        all_attrs.update(item.keys())
    
    # Common attributes first
    ordered_attrs = []
    priority_attrs = ["name", "resource_type", "hourly_price", "cpu_count", "gpu_count", "ram"]
    
    for attr in priority_attrs:
        if attr in all_attrs:
            ordered_attrs.append(attr)
            all_attrs.remove(attr)
    
    ordered_attrs.extend(sorted(all_attrs))
    
    # Add attribute column
    table.add_column("Attribute", style="bright_white", no_wrap=True)
    
    # Add columns for each item
    for item in items:
        table.add_column(
            item.get("name", "N/A"), 
            style="white", 
            justify="center"
        )
    
    # Add rows for each attribute
    for attr in ordered_attrs:
        if attr == "id":  # Skip ID in comparison
            continue
            
        row = [format_attribute_name(attr)]
        for item in items:
            value = item.get(attr, "N/A")
            row.append(format_attribute_value(attr, value))
        
        table.add_row(*row)
    
    return table


def format_status(status: str) -> str:
    """Format status with appropriate colors."""
    status_lower = status.lower()
    
    status_colors = {
        "running": "[green]●[/green] Running",
        "stopped": "[red]●[/red] Stopped",
        "pending": "[yellow]●[/yellow] Pending",
        "starting": "[yellow]●[/yellow] Starting",
        "stopping": "[yellow]●[/yellow] Stopping",
        "terminated": "[dim]●[/dim] Terminated",
        "available": "[green]●[/green] Available",
        "unavailable": "[red]●[/red] Unavailable",
        "maintenance": "[yellow]●[/yellow] Maintenance",
        "error": "[red]●[/red] Error",
        "active": "[green]●[/green] Active",
        "inactive": "[dim]●[/dim] Inactive",
    }
    
    return status_colors.get(status_lower, f"[white]●[/white] {status}")


def format_deployment_status(status: str) -> str:
    """Format deployment status with appropriate colors."""
    status_lower = status.lower()
    
    deployment_colors = {
        "active": "[red]●[/red] In Use",
        "inactive": "[green]●[/green] Available",
        "maintenance": "[yellow]●[/yellow] Maintenance",
        "offline": "[dim]●[/dim] Offline",
    }
    
    return deployment_colors.get(status_lower, f"[white]●[/white] {status.title()}")


def format_price(price: float) -> str:
    """Format price with appropriate styling."""
    if price == 0:
        return "[bright_green]Free[/bright_green]"
    else:
        # Format like "$ /hr" with proper spacing
        return f"[bright_yellow]${price:.2f} /hr[/bright_yellow]"


def format_uptime(created_at: Optional[str]) -> str:
    """Calculate and format uptime."""
    if not created_at:
        return "N/A"
    
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now().astimezone()
        uptime = now - created
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"


def calculate_cost(created_at: Optional[str], price_per_hour: float) -> float:
    """Calculate total cost based on uptime."""
    if not created_at or price_per_hour == 0:
        return 0.0
    
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now().astimezone()
        uptime = now - created
        hours = uptime.total_seconds() / 3600
        return hours * price_per_hour
    except:
        return 0.0


def calculate_hours_ago(timestamp: Optional[str]) -> str:
    """Calculate how many hours ago a timestamp was."""
    if not timestamp or timestamp == "N/A":
        return "Unknown"
    
    try:
        # Handle different timestamp formats
        # API formats: "2025-08-10T05:33:21.400" or "2025-08-15T04:59:06.504065"
        if '.' in timestamp:
            timestamp = timestamp.split('.')[0]  # Remove microseconds
        
        # Handle timezone if present
        if timestamp.endswith('Z'):
            timestamp = timestamp[:-1]  # Remove Z
        
        past_time = datetime.fromisoformat(timestamp)
        now = datetime.now()
        diff = now - past_time
        
        hours = diff.total_seconds() / 3600
        
        if hours < 0:  # Future timestamp
            return "Future"
        elif hours < 1:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}min ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            days = int(hours / 24)
            return f"{days}d ago"
    except Exception as e:
        # For debugging, you might want to see what went wrong
        return "Unknown"


def format_attribute_name(attr: str) -> str:
    """Format attribute names for display."""
    return attr.replace("_", " ").title()


def format_attribute_value(attr: str, value: Any) -> str:
    """Format attribute values for display."""
    if value is None or value == "N/A":
        return "[bright_black]N/A[/bright_black]"
    
    if attr in ["hourly_price", "price_per_hour"]:
        return format_price(float(value))
    elif attr in ["memory_gb", "storage_gb"]:
        return f"[bright_white]{value} GB[/bright_white]"
    elif attr == "ram":
        return f"[bright_white]{str(value)}[/bright_white]"  # Already formatted as "14GB" from API
    elif attr in ["cpu_count", "cpu_cores"]:
        return f"[bright_white]{value} cores[/bright_white]"
    elif attr == "gpu_count":
        return f"[bright_white]{value}x[/bright_white]"
    elif attr == "storage" and isinstance(value, dict):
        return f"[bright_white]{value.get('total_gb', 0)}GB {value.get('type', '')}[/bright_white]"
    elif isinstance(value, bool):
        return "[bright_green]Yes[/bright_green]" if value else "[bright_red]No[/bright_red]"
    elif isinstance(value, dict):
        # For nested objects like network_info, cpu_specs, etc.
        return str(value)
    else:
        return f"[bright_white]{str(value)}[/bright_white]"


def show_table_with_panel(table: Table, subtitle: Optional[str] = None) -> None:
    """Display a table wrapped in a panel."""
    if subtitle:
        panel = Panel(
            table,
            subtitle=f"[bright_white]{subtitle}[/bright_white]",
            subtitle_align="center",
            border_style="bright_cyan",
        )
    else:
        panel = Panel(table, border_style="bright_cyan")
    
    console.print(panel)
