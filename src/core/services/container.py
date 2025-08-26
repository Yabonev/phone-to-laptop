"""Service container for dependency injection."""

import logging
from typing import Dict, Any

from src.infrastructure.storage.json_state import StateService
from src.infrastructure.storage.file_project import ProjectService
from src.infrastructure.transcription.whisper_adapter import TranscriptionService
from src.core.services.cleanup import CleanupService


class ServiceContainer:
    """Container for managing service dependencies."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize all services with configuration."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.state_service = StateService(config.get("state_file", "runtime/data/state.json"))
        self.project_service = ProjectService(
            config.get("projects_dir", "./runtime/data/projects")
        )
        self.transcription_service = TranscriptionService(
            config.get("whisper_model", "large")
        )
        self.cleanup_service = CleanupService(
            audio_dir=config.get("audio_dir", "./runtime/audio")
        )
        
        self.logger.info("Service container initialized")

    def get_all(self) -> Dict[str, Any]:
        """Get all services as a dictionary."""
        return {
            "state": self.state_service,
            "project": self.project_service,
            "transcription": self.transcription_service,
            "cleanup": self.cleanup_service,
        }