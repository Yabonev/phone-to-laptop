"""
State management service - Single Responsibility
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BotState(BaseModel):
    """Bot state model"""
    last_update_id: Optional[int] = None
    active_project: Optional[str] = None
    processed_messages: List[str] = Field(default_factory=list)
    projects: Dict[str, str] = Field(default_factory=dict)
    language: str = "en"


class StateService:
    """Manages bot state persistence"""
    
    def __init__(self, state_file: Path = Path("state.json")):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> BotState:
        """Load state from file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return BotState(**data)
        return BotState()
    
    def save(self) -> None:
        """Save state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state.model_dump(), f, indent=2)
    
    def get_active_project(self) -> Optional[str]:
        """Get current active project ID"""
        return self.state.active_project
    
    def set_active_project(self, project_id: str) -> None:
        """Set active project"""
        self.state.active_project = project_id
        self.save()
    
    def get_language(self) -> str:
        """Get current language setting"""
        return self.state.language
    
    def set_language(self, language: str) -> None:
        """Set language"""
        self.state.language = language
        self.save()
    
    def add_project(self, project_id: str, project_name: str) -> None:
        """Add a new project"""
        self.state.projects[project_id] = project_name
        self.save()
    
    def remove_project(self, project_id: str) -> None:
        """Remove a project"""
        if project_id in self.state.projects:
            del self.state.projects[project_id]
            if self.state.active_project == project_id:
                self.state.active_project = None
            self.save()
    
    def get_projects(self) -> Dict[str, str]:
        """Get all projects"""
        return self.state.projects
    
    def is_message_processed(self, message_id: str) -> bool:
        """Check if message was already processed"""
        return message_id in self.state.processed_messages
    
    def mark_message_processed(self, message_id: str) -> None:
        """Mark message as processed"""
        if message_id not in self.state.processed_messages:
            self.state.processed_messages.append(message_id)
            self.save()
    
    def update_last_update_id(self, update_id: int) -> None:
        """Update last processed update ID"""
        self.state.last_update_id = update_id
        self.save()