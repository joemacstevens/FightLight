"""
Basic tests for FightLight core functionality
"""
import pytest
from hlc_core.models import ProjectState, VideoFile, Highlight, TimeRange


def test_time_range_validation():
    """Test TimeRange model validation"""
    # Valid time range
    time_range = TimeRange(start=10.0, end=20.0)
    assert time_range.start == 10.0
    assert time_range.end == 20.0
    
    # Invalid time range (end <= start)
    with pytest.raises(ValueError):
        TimeRange(start=20.0, end=10.0)
    
    with pytest.raises(ValueError):
        TimeRange(start=10.0, end=10.0)


def test_video_file_model():
    """Test VideoFile model"""
    video = VideoFile(path="/path/to/video.mp4")
    assert video.path == "/path/to/video.mp4"
    assert video.duration is None
    
    video_with_metadata = VideoFile(
        path="/path/to/video.mp4",
        duration=120.5,
        fps=30.0,
        width=1920,
        height=1080
    )
    assert video_with_metadata.duration == 120.5
    assert video_with_metadata.fps == 30.0


def test_highlight_model():
    """Test Highlight model"""
    time_range = TimeRange(start=10.0, end=20.0)
    highlight = Highlight(
        id="test-123",
        name="Test Highlight",
        time_range=time_range,
        description="A test highlight",
        tags=["test", "demo"]
    )
    
    assert highlight.id == "test-123"
    assert highlight.name == "Test Highlight"
    assert highlight.time_range.start == 10.0
    assert highlight.time_range.end == 20.0
    assert highlight.description == "A test highlight"
    assert "test" in highlight.tags


def test_project_state():
    """Test ProjectState model and methods"""
    project = ProjectState(project_name="Test Project")
    assert project.project_name == "Test Project"
    assert len(project.highlights) == 0
    assert project.selected_highlight_id is None
    
    # Add a highlight
    time_range = TimeRange(start=5.0, end=15.0)
    highlight = Highlight(
        id="highlight-1",
        name="First Highlight",
        time_range=time_range
    )
    project.add_highlight(highlight)
    
    assert len(project.highlights) == 1
    assert project.highlights[0].id == "highlight-1"
    
    # Select highlight
    project.selected_highlight_id = "highlight-1"
    selected = project.get_selected_highlight()
    assert selected is not None
    assert selected.id == "highlight-1"
    
    # Remove highlight
    removed = project.remove_highlight("highlight-1")
    assert removed is True
    assert len(project.highlights) == 0
    assert project.selected_highlight_id is None
    
    # Try to remove non-existent highlight
    removed = project.remove_highlight("non-existent")
    assert removed is False


def test_project_state_serialization():
    """Test that ProjectState can be serialized to/from JSON"""
    project = ProjectState(project_name="Serialization Test")
    
    # Add video file
    video = VideoFile(path="/test/video.mp4", duration=60.0)
    project.video_file = video
    
    # Add highlight
    time_range = TimeRange(start=10.0, end=25.0)
    highlight = Highlight(
        id="serialize-test",
        name="Serialization Highlight",
        time_range=time_range,
        description="Test serialization"
    )
    project.add_highlight(highlight)
    
    # Serialize to dict
    data = project.model_dump()
    assert data["project_name"] == "Serialization Test"
    assert data["video_file"]["path"] == "/test/video.mp4"
    assert len(data["highlights"]) == 1
    
    # Deserialize from dict
    restored_project = ProjectState.model_validate(data)
    assert restored_project.project_name == "Serialization Test"
    assert restored_project.video_file.path == "/test/video.mp4"
    assert len(restored_project.highlights) == 1
    assert restored_project.highlights[0].name == "Serialization Highlight"