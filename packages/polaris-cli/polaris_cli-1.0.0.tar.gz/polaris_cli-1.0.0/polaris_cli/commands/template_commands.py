"""
Template management commands
"""

from typing import Optional

import typer
from rich.console import Console

from polaris_cli.auth.token_manager import TokenManager
from polaris_cli.ui.banner import show_loading_spinner, show_success_message
from polaris_cli.ui.tables import show_table_with_panel
from polaris_cli.utils.exceptions import AuthenticationError, PolarisError

app = typer.Typer(help="Template management")
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
def list_templates(
    category: Optional[str] = typer.Option(None, "--category", help="Filter by category"),
    search: Optional[str] = typer.Option(None, "--search", help="Search term"),
    gpu_required: Optional[bool] = typer.Option(None, "--gpu-required", help="Filter by GPU requirement"),
    sort_by: str = typer.Option("name", "--sort-by", help="Sort by (name|category)"),
    output: str = typer.Option("table", "--output", help="Output format (table|json|csv)")
) -> None:
    """List available templates."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print("[cyan]Loading templates...[/cyan]")
    show_loading_spinner("Fetching template data", 1.0)
    
    try:
        # Get authenticated API client and fetch templates
        api_client = token_manager.get_authenticated_api_client()
        
        if search:
            # Use search endpoint if search term provided
            response = api_client.search_templates(query=search, category=category)
        else:
            # Use regular list endpoint
            response = api_client.list_templates(
                category=category,
                gpu_required=gpu_required,
                sort_by=sort_by
            )
        
        templates = response.get("templates", [])
        
        if not templates:
            console.print("[yellow]No templates found matching your criteria[/yellow]")
            return
        
        # Display results based on output format
        if output == "json":
            console.print_json(data=templates)
        elif output == "csv":
            # Output as CSV format for templates
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow([
                "id", "name", "category", "description", "image", "docker_hub",
                "gpu_required", "cpu_compatible", "gpu_compatible",
                "min_ram", "min_storage", "tags", "created_at", "updated_at"
            ])
            
            # Write data rows
            for template in templates:
                requirements = template.get("requirements", {})
                compatibility = template.get("compatibility", {})
                tags = template.get("tags", [])
                
                writer.writerow([
                    template.get("id", ""),
                    template.get("name", ""),
                    template.get("category", ""),
                    template.get("description", ""),
                    template.get("image", ""),
                    template.get("docker_hub", ""),
                    requirements.get("gpu_required", False),
                    compatibility.get("cpu", False),
                    compatibility.get("gpu", False),
                    requirements.get("min_ram", ""),
                    requirements.get("min_storage", ""),
                    ", ".join(tags) if tags else "",
                    template.get("created_at", ""),
                    template.get("updated_at", "")
                ])
            
            console.print(output_buffer.getvalue().strip())
        else:
            # Display as table
            from rich.table import Table
            from rich.text import Text
            
            table = Table(
                title="[bright_white]Templates[/bright_white]", 
                show_lines=True, 
                width=120,
                header_style="bright_white",
                border_style="bright_cyan"
            )
            table.add_column("Template ID", style="bright_cyan", width=25, no_wrap=False)
            table.add_column("Name & Image", style="bright_blue", width=45)
            table.add_column("Requirements", style="bright_green", width=30)
            table.add_column("Category", style="bright_yellow", width=20)
            
            for template in templates:
                # Format name and image from real API structure
                name = template.get("name", "")
                image = template.get("image", "")
                
                # Format image with line breaks if long
                if image and len(image) > 25:
                    # Break long image names at appropriate points
                    if ":" in image:
                        # Split at the colon (before tag) - most common case
                        image_parts = image.split(":")
                        image_display = f"{image_parts[0]}:\n{':'.join(image_parts[1:])}"
                    elif "/" in image:
                        # Split at slash - find the best breaking point
                        parts = image.split("/")
                        if len(parts) >= 3:
                            # For images like "registry/user/image:tag", break after first slash
                            image_display = f"{parts[0]}/\n{'/'.join(parts[1:])}"
                        elif len(parts) == 2:
                            # For images like "user/image:tag", break at slash
                            image_display = f"{parts[0]}/\n{parts[1]}"
                        else:
                            image_display = image
                    else:
                        # No good breaking point found, show as is
                        image_display = image
                else:
                    image_display = image
                
                name_display = f"[bold]{name}[/bold]\n[bright_cyan]{image_display}[/bright_cyan]" if image_display else f"[bold]{name}[/bold]"
                
                # Format requirements and compatibility from real API structure
                requirements_list = []
                requirements = template.get("requirements", {})
                compatibility = template.get("compatibility", {})
                
                # GPU requirement from real API
                gpu_required = requirements.get("gpu_required", False)
                cpu_compatible = compatibility.get("cpu", False)
                gpu_compatible = compatibility.get("gpu", False)
                
                if gpu_required:
                    requirements_list.append("[bright_red]GPU Required[/bright_red]")
                elif gpu_compatible and cpu_compatible:
                    requirements_list.append("[bright_green]CPU + GPU[/bright_green]")
                elif cpu_compatible:
                    requirements_list.append("[bright_blue]CPU Compatible[/bright_blue]")
                else:
                    requirements_list.append("[bright_yellow]Unknown[/bright_yellow]")
                
                # Add resource requirements
                min_ram = requirements.get("min_ram", "")
                min_storage = requirements.get("min_storage", "")
                if min_ram:
                    requirements_list.append(f"[bright_white]RAM: {min_ram}[/bright_white]")
                if min_storage:
                    requirements_list.append(f"[bright_white]Storage: {min_storage}[/bright_white]")
                
                requirements_display = "\n".join(requirements_list)
                
                template_id = template.get("id", "")
                category = template.get("category", "")
                
                table.add_row(
                    template_id,
                    name_display,
                    requirements_display,
                    category
                )
            
            show_table_with_panel(table, f"Found {len(templates)} template(s)")
        
    except PolarisError as e:
        console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("get")
def get_template(
    template_id: str = typer.Argument(..., help="Template ID")
) -> None:
    """Get detailed information about a template."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print(f"[cyan]Loading template [bold]{template_id}[/bold]...[/cyan]")
    show_loading_spinner("Fetching template details", 1.0)
    
    try:
        # Get authenticated API client and fetch template
        api_client = token_manager.get_authenticated_api_client()
        template = api_client.get_template(template_id)
        
        from rich.table import Table
        table = Table(
            title=f"[bright_white]Template Details - {template_id}[/bright_white]", 
            show_header=False,
            header_style="bright_white",
            border_style="bright_cyan"
        )
        table.add_column("Field", style="bright_cyan", no_wrap=True)
        table.add_column("Value", style="bright_white")
        
        # Format and display template details from real API structure
        requirements = template.get("requirements", {})
        compatibility = template.get("compatibility", {})
        
        # Basic info with colors
        details = []
        
        template_id = template.get('id', '')
        if template_id:
            details.append(("ID", f"[bright_white]{template_id}[/bright_white]"))
            
        name = template.get('name', '')
        if name:
            details.append(("Name", f"[bright_white]{name}[/bright_white]"))
        
        category = template.get('category', '')
        if category:
            details.append(("Category", f"[bright_yellow]{category}[/bright_yellow]"))
            
        description = template.get('description', '')
        if description:
            details.append(("Description", f"[bright_white]{description}[/bright_white]"))
            
        image = template.get('image', '')
        if image:
            details.append(("Docker Image", f"[bright_blue]{image}[/bright_blue]"))
            
        docker_hub = template.get('docker_hub', '')
        if docker_hub:
            details.append(("Docker Hub", f"[bright_green]{docker_hub}[/bright_green]"))
        
        # Requirements from real API
        gpu_required = requirements.get("gpu_required", False)
        details.append(("GPU Required", "[bright_green]Yes[/bright_green]" if gpu_required else "[bright_red]No[/bright_red]"))
        
        min_ram = requirements.get("min_ram", "")
        if min_ram:
            details.append(("Minimum RAM", f"[bright_yellow]{min_ram}[/bright_yellow]"))
        
        min_storage = requirements.get("min_storage", "")
        if min_storage:
            details.append(("Minimum Storage", f"[bright_yellow]{min_storage}[/bright_yellow]"))
        
        # Compatibility from real API
        cpu_compatible = compatibility.get("cpu", False)
        gpu_compatible = compatibility.get("gpu", False)
        details.append(("CPU Compatible", "[bright_green]Yes[/bright_green]" if cpu_compatible else "[bright_red]No[/bright_red]"))
        details.append(("GPU Compatible", "[bright_green]Yes[/bright_green]" if gpu_compatible else "[bright_red]No[/bright_red]"))
        
        # Tags
        tags = template.get("tags", [])
        if tags:
            colored_tags = [f"[bright_cyan]{tag}[/bright_cyan]" for tag in tags]
            details.append(("Tags", ", ".join(colored_tags)))
        
        # Timestamps
        created_at = template.get("created_at", "")
        if created_at:
            details.append(("Created", f"[bright_magenta]{created_at[:19]}[/bright_magenta]"))
        
        updated_at = template.get("updated_at", "")
        if updated_at:
            details.append(("Updated", f"[bright_magenta]{updated_at[:19]}[/bright_magenta]"))
        
        for field, value in details:
            # All values are already checked for emptiness when building the details list
            table.add_row(field, value)  # Don't convert to string to preserve Rich markup
        
        show_table_with_panel(table)
        
    except PolarisError as e:
        if "not found" in str(e).lower():
            console.print(f"[red]Template '{template_id}' not found[/red]")
        else:
            console.print(f"[red]API Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("create")
def create_template(
    name: str = typer.Argument(..., help="Template name"),
    from_instance: Optional[str] = typer.Option(None, "--from-instance", help="Create from existing instance"),
    image: str = typer.Option("ubuntu:22.04", "--image", help="Base container image"),
    category: str = typer.Option("Custom", "--category", help="Template category")
) -> None:
    """Create a new template."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print(f"[cyan]Template creation requested for '[bold]{name}[/bold]'...[/cyan]")
    
    # Template creation is typically an admin operation
    # Since the API doesn't expose template creation endpoints to regular users,
    # we'll provide guidance on how to request template creation
    console.print("\n[yellow]Template creation is an admin-only operation.[/yellow]")
    console.print("[dim]Please contact your Polaris administrator to request custom templates.[/dim]")
    console.print(f"\n[dim]Template details to provide:[/dim]")
    console.print(f"  • Name: {name}")
    console.print(f"  • Base Image: {image}")
    console.print(f"  • Category: {category}")
    if from_instance:
        console.print(f"  • Source Instance: {from_instance}")
    
    console.print("\n[dim]In the meantime, you can browse available templates with:[/dim]")
    console.print("  [bold]polaris templates list[/bold]")


@app.command("delete")
def delete_template(
    template_id: str = typer.Argument(..., help="Template ID to delete")
) -> None:
    """Delete a template."""
    
    # Check authentication first
    token_manager = require_authentication()
    
    console.print(f"[cyan]Template deletion requested for '[bold]{template_id}[/bold]'...[/cyan]")
    
    # Template deletion is typically an admin operation
    # Since the API doesn't expose template deletion endpoints to regular users,
    # we'll provide guidance on how to request template deletion
    console.print("\n[yellow]Template deletion is an admin-only operation.[/yellow]")
    console.print("[dim]Please contact your Polaris administrator to request template deletion.[/dim]")
    console.print(f"\n[dim]Template to delete: {template_id}[/dim]")
    
    console.print("\n[dim]You can view template details with:[/dim]")
    console.print(f"  [bold]polaris templates get {template_id}[/bold]")
