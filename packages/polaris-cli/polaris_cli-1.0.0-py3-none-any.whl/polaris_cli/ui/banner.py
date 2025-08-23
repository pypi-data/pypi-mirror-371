"""
Beautiful banner and branding for Polaris CLI
"""

import time
from typing import Optional

from polaris_cli import __version__
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

console = Console()


def show_banner() -> None:
    """Display the main Polaris CLI banner."""
    
    # ASCII art logo
    logo = r"""
    ██████   ██████  ██       █████  ██████  ██ ███████ 
    ██   ██ ██    ██ ██      ██   ██ ██   ██ ██ ██      
    ██████  ██    ██ ██      ███████ ██████  ██ ███████ 
    ██      ██    ██ ██      ██   ██ ██   ██ ██      ██ 
    ██       ██████  ███████ ██   ██ ██   ██ ██ ███████ 
    """
    
    # Create styled logo
    logo_text = Text(logo, style="bold cyan")
    
    # Version and description
    version_text = Text(f"v{__version__}", style="dim")
    description = Text("Cloud Resource Management CLI", style="italic")
    
    # Create the banner panel
    banner_content = Align.center(
        Text.assemble(
            logo_text,
            "\n",
            version_text,
            " • ",
            description,
        )
    )
    
    banner_panel = Panel(
        banner_content,
        style="cyan",
        border_style="bright_cyan",
        title="[bold white]Welcome to Polaris[/bold white]",
        title_align="center",
        subtitle="[dim]The Future of Cloud Computing[/dim]",
        subtitle_align="center",
    )
    
    console.print(banner_panel)


def show_version() -> None:
    """Display version information."""
    version_info = f"""
[bold cyan]Polaris CLI[/bold cyan] [dim]v{__version__}[/dim]

A beautiful cloud resource management interface.

[dim]Repository:[/dim] https://github.com/polaris-team/polaris-cli
[dim]Documentation:[/dim] https://docs.polaris.dev
[dim]Support:[/dim] team@polaris.dev
    """.strip()
    
    console.print(Panel(
        version_info,
        style="cyan",
        border_style="bright_cyan",
        title="[bold white]Version Information[/bold white]",
        title_align="center",
    ))


def show_loading_spinner(message: str = "Loading", duration: float = 2.0) -> None:
    """Show a loading spinner animation."""
    from rich.live import Live
    from rich.spinner import Spinner
    
    with Live(Spinner("dots", text=f"[cyan]{message}...[/cyan]"), refresh_per_second=10) as live:
        time.sleep(duration)
        live.update(f"[green]✓[/green] {message} complete!")
        time.sleep(0.3)  # Brief pause to see the completion message


def show_progress_bar(steps: list[str], delay: float = 0.5) -> None:
    """Show a step-by-step progress animation."""
    for i, step in enumerate(steps, 1):
        console.print(f"[cyan]Step {i}/{len(steps)}:[/cyan] {step}")
        
        # Simple progress bar
        progress = "█" * i + "░" * (len(steps) - i)
        percentage = int((i / len(steps)) * 100)
        
        console.print(f"[bright_cyan][{progress}][/bright_cyan] {percentage}%")
        
        if i < len(steps):
            time.sleep(delay)
        
        console.print()


def show_success_message(message: str) -> None:
    """Display a success message with styling."""
    console.print(Panel(
        f"[green]✓[/green] {message}",
        style="green",
        border_style="bright_green",
        title="[bold white]Success[/bold white]",
        title_align="center",
    ))


def show_error_message(message: str, details: Optional[str] = None) -> None:
    """Display an error message with styling."""
    content = f"[red]✗[/red] {message}"
    if details:
        content += f"\n\n[dim]{details}[/dim]"
    
    console.print(Panel(
        content,
        style="red",
        border_style="bright_red",
        title="[bold white]Error[/bold white]",
        title_align="center",
    ))


def show_warning_message(message: str) -> None:
    """Display a warning message with styling."""
    console.print(Panel(
        f"[yellow]⚠[/yellow] {message}",
        style="yellow",
        border_style="bright_yellow",
        title="[bold white]Warning[/bold white]",
        title_align="center",
    ))


def show_info_box(title: str, content: str, style: str = "blue") -> None:
    """Display an information box."""
    console.print(Panel(
        content,
        style=style,
        border_style=f"bright_{style}",
        title=f"[bold white]{title}[/bold white]",
        title_align="center",
    ))
