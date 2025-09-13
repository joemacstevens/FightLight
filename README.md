# FightLight

A local-first tool for cutting boxing highlights. Ingest video + JSON, cut with PyAV/ffmpeg, preview & export with a simple web UI.

## Features

- **JSON-first approach**: All project state is stored in `project_state.json`
- **Web UI**: Flask-based interface for editing highlights
- **CLI interface**: Typer-based command line tool
- **Local-first**: No external dependencies, works offline
- **Export-only cutting**: Video processing happens only on export

## Quick Start

### Installation

```bash
pip install -e .
```

### Using the CLI

```bash
# Initialize a new project
fightlight init "My Boxing Highlights"

# Import a video file
fightlight import-video /path/to/video.mp4

# Add a highlight
fightlight add-highlight "Great Combo" 30.0 45.5 --desc "Amazing left-right combination"

# List highlights
fightlight highlights

# Start the web UI
fightlight web
```

### Using the Web UI

1. Start the web server: `fightlight web`
2. Open http://localhost:5000 in your browser
3. Import videos and highlights
4. Edit highlight ranges using the web interface
5. Export clips when ready

## Project Structure

- `hlc_core/` - Core data models and business logic
- `hlc_ui/` - Flask web interface
- `hlc_cli/` - Typer command line interface
- `tests/` - Test suite
- `media/` - Video files (local storage)
- `exports/` - Exported clips (gitignored)

## API Endpoints

- `GET /` - Main web interface
- `GET /state` - Get current project state as JSON
- `POST /import/video` - Import a video file
- `POST /import/highlights` - Import highlights from JSON
- `POST /select` - Select a highlight for editing
- `POST /update-range` - Update highlight time range
- `POST /nudge` - Nudge highlight timing
- `POST /export/clip` - Export selected highlight
- `POST /export/all` - Export all highlights

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Start development server
python -m hlc_ui.app
```