"""
Pydantic models for FightLight project state and data structures
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from pathlib import Path


class TimeRange(BaseModel):
    """Represents a time range in seconds"""
    start: float = Field(ge=0, description="Start time in seconds")
    end: float = Field(gt=0, description="End time in seconds")
    
    def model_post_init(self, __context):
        if self.end <= self.start:
            raise ValueError("End time must be greater than start time")


class VideoFile(BaseModel):
    """Represents a video file in the project"""
    path: str = Field(description="Path to the video file")
    duration: Optional[float] = Field(default=None, description="Duration in seconds")
    fps: Optional[float] = Field(default=None, description="Frames per second")
    width: Optional[int] = Field(default=None, description="Video width")
    height: Optional[int] = Field(default=None, description="Video height")


class Highlight(BaseModel):
    """Represents a highlight clip with metadata"""
    id: str = Field(description="Unique identifier for the highlight")
    name: str = Field(description="Human-readable name for the highlight")
    time_range: TimeRange = Field(description="Time range of the highlight")
    description: Optional[str] = Field(default=None, description="Description of the highlight")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class ProjectState(BaseModel):
    """Main project state - the JSON-first data structure"""
    project_name: str = Field(description="Name of the project")
    video_file: Optional[VideoFile] = Field(default=None, description="Main video file")
    highlights: List[Highlight] = Field(default_factory=list, description="List of highlights")
    selected_highlight_id: Optional[str] = Field(default=None, description="Currently selected highlight")
    export_settings: dict = Field(default_factory=dict, description="Export configuration")
    
    def get_selected_highlight(self) -> Optional[Highlight]:
        """Get the currently selected highlight"""
        if not self.selected_highlight_id:
            return None
        for highlight in self.highlights:
            if highlight.id == self.selected_highlight_id:
                return highlight
        return None
    
    def add_highlight(self, highlight: Highlight) -> None:
        """Add a highlight to the project"""
        self.highlights.append(highlight)
    
    def remove_highlight(self, highlight_id: str) -> bool:
        """Remove a highlight by ID. Returns True if removed, False if not found"""
        for i, highlight in enumerate(self.highlights):
            if highlight.id == highlight_id:
                self.highlights.pop(i)
                if self.selected_highlight_id == highlight_id:
                    self.selected_highlight_id = None
                return True
        return False