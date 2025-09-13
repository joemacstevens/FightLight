"""
Flask application for FightLight web UI
"""
import json
import os
from pathlib import Path
from typing import Optional

from flask import Flask, request, jsonify, render_template_string
from hlc_core import ProjectState, VideoFile, Highlight, TimeRange


# Default project state file location
PROJECT_STATE_PATH = Path("project_state.json")

# Simple HTML template for the main UI
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FightLight - Boxing Highlight Cutter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
        button { margin: 5px; padding: 10px; }
        input, textarea { margin: 5px; padding: 5px; }
        .highlight { background: #f0f0f0; margin: 10px 0; padding: 10px; }
    </style>
</head>
<body>
    <h1>FightLight - Boxing Highlight Cutter</h1>
    
    <div class="section">
        <h2>Project State</h2>
        <p>Current project: <span id="project-name">{{ project.project_name if project else "No project loaded" }}</span></p>
        <p>Video file: <span id="video-file">{{ project.video_file.path if project and project.video_file else "No video loaded" }}</span></p>
        <button onclick="location.href='/state'">View Full State (JSON)</button>
    </div>
    
    <div class="section">
        <h2>Import</h2>
        <button onclick="importVideo()">Import Video</button>
        <button onclick="importHighlights()">Import Highlights</button>
    </div>
    
    <div class="section">
        <h2>Highlights</h2>
        <div id="highlights">
            {% if project and project.highlights %}
                {% for highlight in project.highlights %}
                <div class="highlight">
                    <strong>{{ highlight.name }}</strong> ({{ highlight.time_range.start }}s - {{ highlight.time_range.end }}s)
                    <br>{{ highlight.description or "No description" }}
                    <br><button onclick="selectHighlight('{{ highlight.id }}')">Select</button>
                </div>
                {% endfor %}
            {% else %}
                <p>No highlights loaded</p>
            {% endif %}
        </div>
    </div>
    
    <div class="section">
        <h2>Edit Selected Highlight</h2>
        <button onclick="updateRange()">Update Range</button>
        <button onclick="nudge()">Nudge</button>
    </div>
    
    <div class="section">
        <h2>Export</h2>
        <button onclick="exportClip()">Export Selected Clip</button>
        <button onclick="exportAll()">Export All Highlights</button>
    </div>

    <script>
        function importVideo() { alert('Import Video - Feature coming soon'); }
        function importHighlights() { alert('Import Highlights - Feature coming soon'); }
        function selectHighlight(id) { 
            fetch('/select', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({highlight_id: id})
            }).then(() => location.reload());
        }
        function updateRange() { alert('Update Range - Feature coming soon'); }
        function nudge() { alert('Nudge - Feature coming soon'); }
        function exportClip() { alert('Export Clip - Feature coming soon'); }
        function exportAll() { alert('Export All - Feature coming soon'); }
    </script>
</body>
</html>
"""


def load_project_state() -> Optional[ProjectState]:
    """Load project state from JSON file"""
    if not PROJECT_STATE_PATH.exists():
        return None
    
    try:
        with open(PROJECT_STATE_PATH, 'r') as f:
            data = json.load(f)
        return ProjectState.model_validate(data)
    except Exception as e:
        print(f"Error loading project state: {e}")
        return None


def save_project_state(state: ProjectState) -> bool:
    """Save project state to JSON file"""
    try:
        with open(PROJECT_STATE_PATH, 'w') as f:
            json.dump(state.model_dump(), f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving project state: {e}")
        return False


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Ensure required directories exist
    Path("media").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)
    
    @app.route('/')
    def index():
        """Main UI page"""
        project = load_project_state()
        return render_template_string(MAIN_TEMPLATE, project=project)
    
    @app.route('/state')
    def get_state():
        """Get current project state as JSON"""
        project = load_project_state()
        if project:
            return jsonify(project.model_dump())
        else:
            return jsonify({"error": "No project state found"}), 404
    
    @app.route('/import/video', methods=['POST'])
    def import_video():
        """Import a video file"""
        data = request.get_json()
        video_path = data.get('path')
        
        if not video_path:
            return jsonify({"error": "Video path is required"}), 400
        
        # Create or load project state
        project = load_project_state()
        if not project:
            project = ProjectState(project_name="New Project")
        
        # Set video file (simplified - in real implementation would analyze video)
        project.video_file = VideoFile(path=video_path)
        
        if save_project_state(project):
            return jsonify({"message": "Video imported successfully"})
        else:
            return jsonify({"error": "Failed to save project state"}), 500
    
    @app.route('/import/highlights', methods=['POST'])
    def import_highlights():
        """Import highlights from JSON"""
        data = request.get_json()
        highlights_data = data.get('highlights', [])
        
        project = load_project_state()
        if not project:
            project = ProjectState(project_name="New Project")
        
        # Import highlights
        for highlight_data in highlights_data:
            try:
                highlight = Highlight.model_validate(highlight_data)
                project.add_highlight(highlight)
            except Exception as e:
                return jsonify({"error": f"Invalid highlight data: {e}"}), 400
        
        if save_project_state(project):
            return jsonify({"message": f"Imported {len(highlights_data)} highlights"})
        else:
            return jsonify({"error": "Failed to save project state"}), 500
    
    @app.route('/select', methods=['POST'])
    def select_highlight():
        """Select a highlight by ID"""
        data = request.get_json()
        highlight_id = data.get('highlight_id')
        
        if not highlight_id:
            return jsonify({"error": "highlight_id is required"}), 400
        
        project = load_project_state()
        if not project:
            return jsonify({"error": "No project loaded"}), 404
        
        # Verify highlight exists
        if not any(h.id == highlight_id for h in project.highlights):
            return jsonify({"error": "Highlight not found"}), 404
        
        project.selected_highlight_id = highlight_id
        
        if save_project_state(project):
            return jsonify({"message": "Highlight selected", "selected_id": highlight_id})
        else:
            return jsonify({"error": "Failed to save project state"}), 500
    
    @app.route('/update-range', methods=['POST'])
    def update_range():
        """Update the time range of the selected highlight"""
        data = request.get_json()
        start = data.get('start')
        end = data.get('end')
        
        if start is None or end is None:
            return jsonify({"error": "start and end times are required"}), 400
        
        project = load_project_state()
        if not project:
            return jsonify({"error": "No project loaded"}), 404
        
        selected = project.get_selected_highlight()
        if not selected:
            return jsonify({"error": "No highlight selected"}), 400
        
        try:
            selected.time_range = TimeRange(start=start, end=end)
        except Exception as e:
            return jsonify({"error": f"Invalid time range: {e}"}), 400
        
        if save_project_state(project):
            return jsonify({"message": "Time range updated"})
        else:
            return jsonify({"error": "Failed to save project state"}), 500
    
    @app.route('/nudge', methods=['POST'])
    def nudge():
        """Nudge the selected highlight's time range"""
        data = request.get_json()
        offset = data.get('offset', 1.0)  # Default 1 second nudge
        
        project = load_project_state()
        if not project:
            return jsonify({"error": "No project loaded"}), 404
        
        selected = project.get_selected_highlight()
        if not selected:
            return jsonify({"error": "No highlight selected"}), 400
        
        try:
            new_start = max(0, selected.time_range.start + offset)
            new_end = selected.time_range.end + offset
            selected.time_range = TimeRange(start=new_start, end=new_end)
        except Exception as e:
            return jsonify({"error": f"Invalid nudge operation: {e}"}), 400
        
        if save_project_state(project):
            return jsonify({"message": f"Highlight nudged by {offset}s"})
        else:
            return jsonify({"error": "Failed to save project state"}), 500
    
    @app.route('/export/clip', methods=['POST'])
    def export_clip():
        """Export the selected highlight as a video clip"""
        project = load_project_state()
        if not project:
            return jsonify({"error": "No project loaded"}), 404
        
        selected = project.get_selected_highlight()
        if not selected:
            return jsonify({"error": "No highlight selected"}), 400
        
        if not project.video_file:
            return jsonify({"error": "No video file loaded"}), 400
        
        # TODO: Implement actual video cutting with PyAV/ffmpeg
        output_path = f"exports/{selected.name}_{selected.id}.mp4"
        
        return jsonify({
            "message": "Clip export initiated (stub implementation)",
            "output_path": output_path,
            "highlight": selected.model_dump()
        })
    
    @app.route('/export/all', methods=['POST'])
    def export_all():
        """Export all highlights as separate video clips"""
        project = load_project_state()
        if not project:
            return jsonify({"error": "No project loaded"}), 404
        
        if not project.highlights:
            return jsonify({"error": "No highlights to export"}), 400
        
        if not project.video_file:
            return jsonify({"error": "No video file loaded"}), 400
        
        # TODO: Implement actual video cutting with PyAV/ffmpeg
        output_paths = []
        for highlight in project.highlights:
            output_path = f"exports/{highlight.name}_{highlight.id}.mp4"
            output_paths.append(output_path)
        
        return jsonify({
            "message": f"Export initiated for {len(project.highlights)} highlights (stub implementation)",
            "output_paths": output_paths
        })
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)