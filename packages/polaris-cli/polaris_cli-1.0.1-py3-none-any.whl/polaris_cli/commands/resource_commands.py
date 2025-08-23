"""
Resource discovery and management commands
"""

from typing import List, Optional

import typer
from rich.console import Console

from polaris_cli.auth.token_manager import TokenManager
from polaris_cli.ui.banner import show_info_box, show_loading_spinner
from polaris_cli.ui.tables import (create_comparison_table,
                                   create_resource_table,
                                   show_table_with_panel)
from polaris_cli.utils.exceptions import AuthenticationError, PolarisError

app = typer.Typer(help="Resource discovery and comparison")
console = Console()


def require_authentication() -> TokenManager:
    """Check if user is authenticated, exit if not. Return TokenManager if authenticated."""
    token_manager = TokenManager()
    if not token_manager.is_authenticated():
        console.print("[red]❌ Authentication required![/red]")
        console.print("[yellow]Please login first: [bold]polaris auth login --api-key YOUR_TOKEN[/bold][/yellow]")
        raise typer.Exit(1)
    return token_manager


@app.command("list")
def list_resources(
    resource_type: Optional[str] = typer.Option(None, "--type", help="Filter by resource type (cpu|gpu|storage)"),
    provider: Optional[str] = typer.Option(None, "--provider", help="Filter by provider (amd|intel|nvidia)"),
    region: Optional[str] = typer.Option(None, "--region", help="Filter by region"),
    available_only: bool = typer.Option(False, "--available-only", help="Show only available resources"),
    sort_by: str = typer.Option("price", "--sort-by", help="Sort by (price|performance|availability)"),
    output: str = typer.Option("table", "--output", help="Output format (table|json|csv)")
) -> None:
    """List available cloud resources."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print("[cyan]Discovering resources...[/cyan]")
    show_loading_spinner("Fetching resource data", 1.5)
    
    try:
        # Get authenticated API client and fetch resources
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.list_resources(
            provider=provider,
            resource_type=resource_type,
            available_only=available_only,
            sort_by=sort_by
        )
        
        resources = response.get("resources", [])
        
        if not resources:
            console.print("[yellow]No resources found matching your criteria[/yellow]")
            return
        
        # Display results
        if output == "json":
            console.print_json(data=resources)
        elif output == "csv":
            # Output as CSV format
            import csv
            import io
            
            if not resources:
                console.print("resource_id,resource_type,region,cpu_count,gpu_count,ram,storage,hourly_price,deployment_status")
                return
            
            # Create CSV string
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow([
                "resource_id", "resource_type", "region", "country", "city", 
                "cpu_count", "cpu_model", "cpu_cores", "cpu_threads", "cpu_clock",
                "gpu_count", "gpu_model", "gpu_memory", "ram", "storage_gb", 
                "storage_type", "hourly_price", "deployment_status"
            ])
            
            # Write data rows
            for resource in resources:
                network_info = resource.get("network_info", {})
                cpu_specs = resource.get("cpu_specs", {})
                gpu_specs = resource.get("gpu_specs", {})
                storage_info = resource.get("storage", {})
                
                writer.writerow([
                    resource.get("resource_id", ""),
                    resource.get("resource_type", ""),
                    network_info.get("region", ""),
                    network_info.get("country", ""),
                    network_info.get("city", ""),
                    resource.get("cpu_count", 0),
                    cpu_specs.get("model_name", ""),
                    cpu_specs.get("cores", ""),
                    cpu_specs.get("threads", ""),
                    cpu_specs.get("clock_speed", ""),
                    resource.get("gpu_count", 0),
                    gpu_specs.get("model_name", ""),
                    gpu_specs.get("memory", ""),
                    resource.get("ram", ""),
                    storage_info.get("total_gb", "") if isinstance(storage_info, dict) else "",
                    storage_info.get("type", "") if isinstance(storage_info, dict) else "",
                    resource.get("hourly_price", 0),
                    resource.get("deployment_status", "")
                ])
            
            # Print CSV content
            console.print(output_buffer.getvalue().strip())
        else:
            table = create_resource_table(resources, "Available Resources")
            show_table_with_panel(table, f"Found {len(resources)} resource(s)")
            
    except PolarisError as e:
        console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("cpu")
def cpu_resources() -> None:
    """CPU resource management. Use subcommands like 'cpu-list'."""
    console.print("[cyan]CPU resource commands:[/cyan]")
    console.print("  • polaris resources cpu-list")
    console.print("  • polaris resources cpu-models")
    console.print("  • polaris resources cpu-compare")


@app.command("cpu-list")
def list_cpu_resources(
    provider: Optional[str] = typer.Option(None, "--provider", help="CPU provider (amd|intel)"),
    cores: Optional[str] = typer.Option(None, "--cores", help="Core count range (e.g., '16-64')"),
    architecture: Optional[str] = typer.Option(None, "--architecture", help="Architecture (x86|arm)"),
    output: str = typer.Option("table", "--output", help="Output format (table|json|csv)")
) -> None:
    """List available CPU resources."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print("[cyan]Loading CPU resources...[/cyan]")
    show_loading_spinner("Fetching CPU data", 1.0)
    
    try:
        # Parse cores parameter for API
        min_cores = None
        if cores:
            try:
                if "-" in cores:
                    min_cores, _ = map(int, cores.split("-"))
                else:
                    min_cores = int(cores)
            except ValueError:
                console.print("[red]Invalid cores format. Use single number or 'min-max'[/red]")
                return
        
        # Get authenticated API client and fetch CPU resources
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.list_cpu_resources(
            min_cores=min_cores,
            architecture=architecture,
            available_only=True
        )
        
        resources = response.get("resources", [])
        
        # Apply additional filtering that API doesn't support
        if provider:
            resources = [r for r in resources 
                        if provider.lower() in r.get("cpu_specs", {}).get("model_name", "").lower()]
        
        if cores and "-" in cores:
            try:
                min_cores, max_cores = map(int, cores.split("-"))
                resources = [r for r in resources 
                           if min_cores <= r.get("cpu_count", 0) <= max_cores]
            except ValueError:
                pass
        
        if not resources:
            console.print("[yellow]No CPU resources found matching criteria[/yellow]")
            return
        
        # Display results
        if output == "json":
            console.print_json(data=resources)
        elif output == "csv":
            # Output as CSV format for CPU resources
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow([
                "resource_id", "resource_type", "region", "country", "city",
                "cpu_count", "cpu_model", "cpu_cores", "cpu_threads", "cpu_clock",
                "ram", "storage_gb", "storage_type", "hourly_price", "deployment_status"
            ])
            
            # Write data rows
            for resource in resources:
                network_info = resource.get("network_info", {})
                cpu_specs = resource.get("cpu_specs", {})
                storage_info = resource.get("storage", {})
                
                writer.writerow([
                    resource.get("resource_id", ""),
                    resource.get("resource_type", ""),
                    network_info.get("region", ""),
                    network_info.get("country", ""),
                    network_info.get("city", ""),
                    resource.get("cpu_count", 0),
                    cpu_specs.get("model_name", ""),
                    cpu_specs.get("cores", ""),
                    cpu_specs.get("threads", ""),
                    cpu_specs.get("clock_speed", ""),
                    resource.get("ram", ""),
                    storage_info.get("total_gb", "") if isinstance(storage_info, dict) else "",
                    storage_info.get("type", "") if isinstance(storage_info, dict) else "",
                    resource.get("hourly_price", 0),
                    resource.get("deployment_status", "")
                ])
            
            console.print(output_buffer.getvalue().strip())
        else:
            table = create_resource_table(resources, "CPU Resources")
            show_table_with_panel(table, f"Found {len(resources)} CPU resource(s)")
        
    except PolarisError as e:
        console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("gpu")
def gpu_resources() -> None:
    """GPU resource management. Use subcommands like 'gpu-list'."""
    console.print("[cyan]GPU resource commands:[/cyan]")
    console.print("  • polaris resources gpu-list")
    console.print("  • polaris resources gpu-models") 
    console.print("  • polaris resources gpu-compare")
    console.print("  • polaris resources gpu-benchmark")


@app.command("gpu-list")
def list_gpu_resources(
    provider: Optional[str] = typer.Option(None, "--provider", help="GPU provider (nvidia|amd)"),
    memory: Optional[str] = typer.Option(None, "--memory", help="Memory range (e.g., '8gb-80gb')"),
    compute_capability: Optional[str] = typer.Option(None, "--compute-capability", help="NVIDIA compute capability"),
    tensor_cores: Optional[bool] = typer.Option(None, "--tensor-cores", help="Require tensor cores"),
    output: str = typer.Option("table", "--output", help="Output format (table|json|csv)")
) -> None:
    """List available GPU resources."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print("[cyan]Loading GPU resources...[/cyan]")
    show_loading_spinner("Fetching GPU data", 1.2)
    
    try:
        # Parse memory parameter for API
        min_memory = None
        if memory:
            try:
                # Convert memory formats to API format
                if "+" in memory:
                    min_memory = memory.replace("gb", "GB").replace("+", "")
                elif "-" in memory:
                    min_mem, _ = memory.replace("gb", "").split("-")
                    min_memory = f"{min_mem}GB"
                else:
                    min_memory = memory.replace("gb", "GB")
            except ValueError:
                console.print("[red]Invalid memory format. Use '8gb', '24gb+', or '8gb-80gb'[/red]")
                return
        
        # Get authenticated API client and fetch GPU resources
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.list_gpu_resources(
            provider=provider,
            min_memory=min_memory,
            available_only=True
        )
        
        resources = response.get("resources", [])
        
        # Apply additional filtering that API doesn't support
        if memory and "-" in memory:
            try:
                min_mem, max_mem = memory.replace("gb", "").split("-")
                min_mem, max_mem = int(min_mem), int(max_mem)
                filtered = []
                for r in resources:
                    gpu_memory_str = r.get("gpu_specs", {}).get("memory", "0GB")
                    gpu_memory_gb = int(gpu_memory_str.replace("GB", ""))
                    if min_mem <= gpu_memory_gb <= max_mem:
                        filtered.append(r)
                resources = filtered
            except ValueError:
                pass
        
        if tensor_cores is not None:
            resources = [r for r in resources 
                        if bool(r.get("gpu_specs", {}).get("tensor_cores", 0)) == tensor_cores]
        
        if not resources:
            console.print("[yellow]No GPU resources found matching criteria[/yellow]")
            return
        
        # Display results
        if output == "json":
            console.print_json(data=resources)
        elif output == "csv":
            # Output as CSV format for GPU resources
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow([
                "resource_id", "resource_type", "region", "country", "city",
                "cpu_count", "cpu_model", "cpu_cores", "cpu_threads", "cpu_clock",
                "gpu_count", "gpu_model", "gpu_memory", "gpu_cores", "gpu_clock",
                "ram", "storage_gb", "storage_type", "hourly_price", "deployment_status"
            ])
            
            # Write data rows
            for resource in resources:
                network_info = resource.get("network_info", {})
                cpu_specs = resource.get("cpu_specs", {})
                gpu_specs = resource.get("gpu_specs", {})
                storage_info = resource.get("storage", {})
                
                writer.writerow([
                    resource.get("resource_id", ""),
                    resource.get("resource_type", ""),
                    network_info.get("region", ""),
                    network_info.get("country", ""),
                    network_info.get("city", ""),
                    resource.get("cpu_count", 0),
                    cpu_specs.get("model_name", ""),
                    cpu_specs.get("cores", ""),
                    cpu_specs.get("threads", ""),
                    cpu_specs.get("clock_speed", ""),
                    resource.get("gpu_count", 0),
                    gpu_specs.get("model_name", ""),
                    gpu_specs.get("memory", ""),
                    gpu_specs.get("cores", ""),
                    gpu_specs.get("clock_speed", ""),
                    resource.get("ram", ""),
                    storage_info.get("total_gb", "") if isinstance(storage_info, dict) else "",
                    storage_info.get("type", "") if isinstance(storage_info, dict) else "",
                    resource.get("hourly_price", 0),
                    resource.get("deployment_status", "")
                ])
            
            console.print(output_buffer.getvalue().strip())
        else:
            table = create_resource_table(resources, "GPU Resources")  
            show_table_with_panel(table, f"Found {len(resources)} GPU resource(s)")
        
    except PolarisError as e:
        console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("gpu-compare")
def compare_gpu_models(
    model1: str = typer.Argument(..., help="First GPU model to compare"),
    model2: str = typer.Argument(..., help="Second GPU model to compare"),
    benchmark: Optional[str] = typer.Option("ml", "--benchmark", help="Benchmark type (ml|gaming|mining)")
) -> None:
    """Compare two GPU models."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print(f"[cyan]Comparing [bold]{model1}[/bold] vs [bold]{model2}[/bold]...[/cyan]")
    show_loading_spinner("Loading comparison data", 1.0)
    
    try:
        # Get authenticated API client and search for both GPU models
        api_client = token_manager.get_authenticated_api_client()
        
        # Search for first model
        response1 = api_client.search_resources(query=model1, resource_type="gpu")
        resources1 = response1.get("resources", [])
        
        # Search for second model
        response2 = api_client.search_resources(query=model2, resource_type="gpu") 
        resources2 = response2.get("resources", [])
        
        # Find the best matches
        gpu1 = None
        gpu2 = None
        
        for r in resources1:
            gpu_model = r.get("gpu_specs", {}).get("model_name", "").lower()
            if model1.lower() in gpu_model:
                gpu1 = r
                break
        
        for r in resources2:
            gpu_model = r.get("gpu_specs", {}).get("model_name", "").lower()
            if model2.lower() in gpu_model:
                gpu2 = r
                break
        
        if not gpu1 or not gpu2:
            console.print(f"[yellow]Could not find both GPU models for comparison[/yellow]")
            console.print(f"Try searching with: polaris resources search 'gpu models'")
            return
        
        # Create comparison
        comparison_gpus = [gpu1, gpu2]
        
        table = create_comparison_table(comparison_gpus, f"GPU Comparison - {benchmark.upper()} Performance")
        show_table_with_panel(table, f"Comparing {len(comparison_gpus)} GPU models")
        
    except PolarisError as e:
        console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("search")
def search_resources_command(
    query: str = typer.Argument(..., help="Search query"),
    cpu_provider: Optional[str] = typer.Option(None, "--cpu-provider", help="CPU provider filter"),
    gpu_provider: Optional[str] = typer.Option(None, "--gpu-provider", help="GPU provider filter"),
    price_range: Optional[str] = typer.Option(None, "--price-range", help="Price range (e.g., '1.0-3.0')"),
    location: Optional[str] = typer.Option(None, "--location", help="Location/region filter"),
    output: str = typer.Option("table", "--output", help="Output format (table|json|csv)")
) -> None:
    """Search for resources using natural language queries."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print(f"[cyan]Searching for: '[bold]{query}[/bold]'...[/cyan]")
    show_loading_spinner("Analyzing search query", 1.0)
    
    try:
        # Determine resource type from query
        resource_type = None
        if any(keyword in query.lower() for keyword in ["gpu", "graphics", "cuda", "tensor"]):
            resource_type = "gpu"
        elif any(keyword in query.lower() for keyword in ["cpu", "processor", "compute"]):
            resource_type = "cpu"
        
        # Get authenticated API client and search resources
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.search_resources(
            query=query,
            resource_type=resource_type,
            available_only=True
        )
        
        search_results = response.get("resources", [])
        
        # Apply additional filters
        if cpu_provider:
            search_results = [r for r in search_results 
                             if cpu_provider.lower() in r.get("cpu_specs", {}).get("model_name", "").lower()]
        
        if gpu_provider:
            search_results = [r for r in search_results 
                             if gpu_provider.lower() in r.get("gpu_specs", {}).get("model_name", "").lower()]
        
        if price_range:
            try:
                min_price, max_price = map(float, price_range.split("-"))
                search_results = [r for r in search_results 
                                if min_price <= r.get("hourly_price", 0) <= max_price]
            except ValueError:
                console.print("[red]Invalid price range format. Use 'min-max' (e.g., '1.0-3.0')[/red]")
                return
        
        if location:
            search_results = [r for r in search_results 
                             if location.lower() in r.get("network_info", {}).get("region", "").lower()]
        
        if not search_results:
            console.print(f"[yellow]No resources found for query: '{query}'[/yellow]")
            return
        
        # Display results
        if output == "json":
            console.print_json(data=search_results)
        elif output == "csv":
            # Output as CSV format for search results
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow([
                "resource_id", "resource_type", "region", "country", "city",
                "cpu_count", "cpu_model", "cpu_cores", "cpu_threads", "cpu_clock",
                "gpu_count", "gpu_model", "gpu_memory", "ram", "storage_gb",
                "storage_type", "hourly_price", "deployment_status"
            ])
            
            # Write data rows
            for resource in search_results:
                network_info = resource.get("network_info", {})
                cpu_specs = resource.get("cpu_specs", {})
                gpu_specs = resource.get("gpu_specs", {})
                storage_info = resource.get("storage", {})
                
                writer.writerow([
                    resource.get("resource_id", ""),
                    resource.get("resource_type", ""),
                    network_info.get("region", ""),
                    network_info.get("country", ""),
                    network_info.get("city", ""),
                    resource.get("cpu_count", 0),
                    cpu_specs.get("model_name", ""),
                    cpu_specs.get("cores", ""),
                    cpu_specs.get("threads", ""),
                    cpu_specs.get("clock_speed", ""),
                    resource.get("gpu_count", 0),
                    gpu_specs.get("model_name", ""),
                    gpu_specs.get("memory", ""),
                    resource.get("ram", ""),
                    storage_info.get("total_gb", "") if isinstance(storage_info, dict) else "",
                    storage_info.get("type", "") if isinstance(storage_info, dict) else "",
                    resource.get("hourly_price", 0),
                    resource.get("deployment_status", "")
                ])
            
            console.print(output_buffer.getvalue().strip())
        else:
            table = create_resource_table(search_results, f"Search Results for '{query}'")
            show_table_with_panel(table, f"Found {len(search_results)} matching resource(s)")
        
    except PolarisError as e:
        console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("availability")
def check_availability(
    machine_type: Optional[str] = typer.Option(None, "--machine-type", help="Machine type to check"),
    region: Optional[str] = typer.Option(None, "--region", help="Region to check"),
    forecast: Optional[str] = typer.Option("24h", "--forecast", help="Forecast period (hours|days)")
) -> None:
    """Check resource availability and forecasts."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print("[cyan]Checking resource availability...[/cyan]")
    show_loading_spinner("Fetching availability data", 1.5)
    
    try:
        # Get authenticated API client and fetch availability
        api_client = token_manager.get_authenticated_api_client()
        response = api_client.get_resource_availability(region=region)
        
        statistics = response.get("statistics", {})
        
        availability_info = {
            "total_resources": statistics.get("total_resources", 0),
            "available_resources": statistics.get("available_resources", 0),
            "cpu_resources": statistics.get("cpu_resources", 0),
            "gpu_resources": statistics.get("gpu_resources", 0),
            "average_price": statistics.get("average_hourly_price", 0),
        }
        
        # Calculate availability percentage
        if availability_info["total_resources"] > 0:
            availability_score = availability_info["available_resources"] / availability_info["total_resources"]
        else:
            availability_score = 0
        
        # Determine availability level
        if availability_score >= 0.8:
            availability_level = "High"
        elif availability_score >= 0.5:
            availability_level = "Medium"
        else:
            availability_level = "Low"
        
        show_info_box("Availability Status", 
                      f"Status: {availability_level}\n"
                      f"Available: {availability_info['available_resources']}/{availability_info['total_resources']} resources ({availability_score:.1%})\n"
                      f"CPU Resources: {availability_info['cpu_resources']}\n"
                      f"GPU Resources: {availability_info['gpu_resources']}\n"
                      f"Average Price: ${availability_info['average_price']:.2f}/hour")
        
    except PolarisError as e:
        console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("pricing")
def pricing_info() -> None:
    """Resource pricing information and calculator."""
    console.print("[cyan]Pricing commands:[/cyan]")
    console.print("  • polaris resources pricing-compare")
    console.print("  • polaris resources pricing-trends")  
    console.print("  • polaris resources pricing-calculator")


@app.command("pricing-calculator")
def pricing_calculator(
    machine_type: str = typer.Option(..., "--machine-type", help="Machine type for calculation"),
    duration: str = typer.Option("1h", "--duration", help="Duration (e.g., '24h', '7d')"),
    quantity: int = typer.Option(1, "--quantity", help="Number of instances"),
    discount_code: Optional[str] = typer.Option(None, "--discount-code", help="Discount code")
) -> None:
    """Calculate estimated costs for resource usage."""
    
    console.print(f"[cyan]Calculating costs for [bold]{machine_type}[/bold]...[/cyan]")
    show_loading_spinner("Computing pricing", 1.0)
    
    # Mock pricing calculation
    base_price = 2.50  # per hour
    
    # Parse duration
    duration_hours = 1
    if duration.endswith("h"):
        duration_hours = int(duration[:-1])
    elif duration.endswith("d"):
        duration_hours = int(duration[:-1]) * 24
    elif duration.endswith("w"):
        duration_hours = int(duration[:-1]) * 24 * 7
    
    subtotal = base_price * duration_hours * quantity
    discount = 0.0
    
    if discount_code:
        discount = subtotal * 0.10  # 10% discount
    
    total = subtotal - discount
    
    # Display pricing breakdown
    show_info_box("Cost Calculation",
                  f"Machine Type: {machine_type}\n"
                  f"Duration: {duration} ({duration_hours} hours)\n"
                  f"Quantity: {quantity}\n"
                  f"Base Rate: ${base_price:.2f}/hour\n"
                  f"Subtotal: ${subtotal:.2f}\n"
                  f"Discount: ${discount:.2f}\n"
                  f"Total: ${total:.2f}")
