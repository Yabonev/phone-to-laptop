"""
Dependency injection container - Dependency Inversion Principle
"""

import logging
from pathlib import Path
from typing import Any

from .cleanup import CleanupService
from .project import ProjectService
from .state import StateService
from .transcription import TranscriptionService


class ServiceContainer:
    """Container for all services - enables dependency injection"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._services = {}
        self._initialize_services()

    def _initialize_services(self):
        """Initialize all services"""
        # Logger
        self._services["logger"] = logging.getLogger(__name__)

        # State service
        self._services["state"] = StateService(
            state_file=Path(self.config.get("state_file", "state.json"))
        )

        # Project service
        self._services["project"] = ProjectService(
            projects_dir=Path(self.config.get("projects_dir", "./projects"))
        )

        # Transcription service
        self._services["transcription"] = TranscriptionService(
            model_name=self.config.get("whisper_model", "large"),
            audio_dir=Path(self.config.get("audio_dir", "./audio")),
        )

        # Cleanup service
        self._services["cleanup"] = CleanupService(
            audio_dir=Path(self.config.get("audio_dir", "./audio")),
            logs_dir=Path(self.config.get("logs_dir", "./logs")),
        )

        # Config
        self._services["config"] = self.config

    def get(self, service_name: str) -> Any:
        """Get a service by name"""
        return self._services.get(service_name)

    def get_all(self) -> dict[str, Any]:
        """Get all services for injection"""
        return self._services

    def register(self, name: str, service: Any) -> None:
        """Register a custom service"""
        self._services[name] = service
