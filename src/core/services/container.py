"""Service container for dependency injection."""

import logging
from pathlib import Path
from typing import Any

from src.core.services.cleanup import CleanupService
from src.infrastructure.storage.file_project import ProjectService
from src.infrastructure.storage.json_state import StateService
from src.infrastructure.transcription.whisper_adapter import TranscriptionService


class ServiceContainer:
    """Container for managing service dependencies."""

    def __init__(self, config: dict[str, Any]):
        """Initialize all services with configuration."""
        self.logger = logging.getLogger(__name__)
        self.config = config  # Store config for access

        # Initialize services - convert paths to Path objects
        self.state_service = StateService(Path(config.get("state_file", "runtime/data/state.json")))
        self.project_service = ProjectService(
            Path(config.get("projects_dir", "./runtime/data/projects"))
        )
        self.transcription_service = TranscriptionService(config.get("whisper_model", "large"))
        self.cleanup_service = CleanupService(
            audio_dir=Path(config.get("audio_dir", "./runtime/audio")),
            logs_dir=Path(config.get("logs_dir", "./runtime/logs")),
        )

        self.logger.info("Service container initialized")

    def get_all(self) -> dict[str, Any]:
        """Get all services as a dictionary."""
        return {
            "state": self.state_service,
            "project": self.project_service,
            "transcription": self.transcription_service,
            "cleanup": self.cleanup_service,
            "logger": logging.getLogger("bot"),  # Provide a logger instance
            "config": self.config,  # Provide access to config
        }

    def get(self, service_name: str) -> Any:
        """Get a specific service by name."""
        # First check if it's a custom registered service
        custom_service = getattr(self, f"{service_name}_service", None)
        if custom_service is not None:
            return custom_service
        
        # Otherwise check default services
        services = self.get_all()
        return services.get(service_name)

    def register(self, name: str, service: Any) -> None:
        """Register a custom service."""
        setattr(self, f"{name}_service", service)
