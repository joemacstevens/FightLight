"""
FightLight CLI - Command line interface using Typer
"""
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from hlc_core import ProjectState, VideoFile, Highlight, TimeRange

app = typer.Typer(help="FightLight - Boxing highlight cutter CLI")
console = Console()

PROJECT_STATE_PATH = Path("project_state.json")


def load_project_state() -> Optional[ProjectState]:
    """Load project state from JSON file"""
    if not PROJECT_STATE_PATH.exists():
        return None
    
    try:
        with open(PROJECT_STATE_PATH, 'r') as f:
            data = json.load(f)
        return ProjectState.model_validate(data)
    except Exception as e:
        console.print(f"[red]Error loading project state: {e}[/red]")
        return None


def save_project_state(state: ProjectState) -> bool:
    """Save project state to JSON file"""
    try:
        with open(PROJECT_STATE_PATH, 'w') as f:
            json.dump(state.model_dump(), f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red]Error saving project state: {e}[/red]")
        return False


@app.command()
def init(name: str = typer.Argument(..., help="Project name")):
    """Initialize a new FightLight project"""
    if PROJECT_STATE_PATH.exists():
        overwrite = typer.confirm("Project state file already exists. Overwrite?")
        if not overwrite:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit()
    
    project = ProjectState(project_name=name)
    
    if save_project_state(project):
        console.print(f"[green]Initialized project: {name}[/green]")
    else:
        console.print("[red]Failed to initialize project[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show current project status"""
    project = load_project_state()
    
    if not project:
        console.print("[red]No project found. Run 'fightlight init <name>' to create one.[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold]Project:[/bold] {project.project_name}")
    
    if project.video_file:
        console.print(f"[bold]Video:[/bold] {project.video_file.path}")
        if project.video_file.duration:
            console.print(f"[bold]Duration:[/bold] {project.video_file.duration}s")
    else:
        console.print("[yellow]No video file loaded[/yellow]")
    
    console.print(f"[bold]Highlights:[/bold] {len(project.highlights)}")
    
    if project.selected_highlight_id:
        selected = project.get_selected_highlight()
        if selected:
            console.print(f"[bold]Selected:[/bold] {selected.name}")


@app.command()
def highlights():
    """List all highlights in the project"""
    project = load_project_state()
    
    if not project:
        console.print("[red]No project found[/red]")
        raise typer.Exit(1)
    
    if not project.highlights:
        console.print("[yellow]No highlights found[/yellow]")
        return
    
    table = Table(title="Highlights")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Start", style="green")
    table.add_column("End", style="green")
    table.add_column("Duration", style="blue")
    table.add_column("Selected", style="yellow")
    
    for highlight in project.highlights:
        duration = highlight.time_range.end - highlight.time_range.start
        selected = "✓" if highlight.id == project.selected_highlight_id else ""
        table.add_row(
            highlight.id,
            highlight.name,
            f"{highlight.time_range.start:.1f}s",
            f"{highlight.time_range.end:.1f}s",
            f"{duration:.1f}s",
            selected
        )
    
    console.print(table)


@app.command()
def import_video(path: str = typer.Argument(..., help="Path to video file")):
    """Import a video file into the project"""
    video_path = Path(path)
    
    if not video_path.exists():
        console.print(f"[red]Video file not found: {path}[/red]")
        raise typer.Exit(1)
    
    project = load_project_state()
    if not project:
        console.print("[red]No project found. Run 'fightlight init <name>' first.[/red]")
        raise typer.Exit(1)
    
    # TODO: Use PyAV to analyze video properties
    project.video_file = VideoFile(path=str(video_path))
    
    if save_project_state(project):
        console.print(f"[green]Video imported: {path}[/green]")
    else:
        console.print("[red]Failed to import video[/red]")
        raise typer.Exit(1)


@app.command()
def add_highlight(
    name: str = typer.Argument(..., help="Highlight name"),
    start: float = typer.Argument(..., help="Start time in seconds"),
    end: float = typer.Argument(..., help="End time in seconds"),
    description: Optional[str] = typer.Option(None, "--desc", help="Description")
):
    """Add a new highlight to the project"""
    project = load_project_state()
    if not project:
        console.print("[red]No project found[/red]")
        raise typer.Exit(1)
    
    try:
        import uuid
        highlight_id = str(uuid.uuid4())[:8]
        time_range = TimeRange(start=start, end=end)
        highlight = Highlight(
            id=highlight_id,
            name=name,
            time_range=time_range,
            description=description
        )
        project.add_highlight(highlight)
        
        if save_project_state(project):
            console.print(f"[green]Added highlight: {name} ({start}s - {end}s)[/green]")
        else:
            console.print("[red]Failed to save highlight[/red]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error adding highlight: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def web():
    """Start the web UI server"""
    try:
        from hlc_ui import create_app
        app = create_app()
        console.print("[green]Starting web UI server at http://localhost:5000[/green]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError:
        console.print("[red]Flask not available. Install with: pip install flask[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")


if __name__ == "__main__":
    app()