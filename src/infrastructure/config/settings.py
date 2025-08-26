"""Application configuration and settings."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """Application settings."""

    # Telegram settings
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")

    # Whisper settings
    whisper_model: str = os.getenv("WHISPER_MODEL", "large")

    # Directory settings
    projects_dir: Path = Path(os.getenv("PROJECTS_DIR", "./runtime/data/projects"))
    audio_dir: Path = Path(os.getenv("AUDIO_DIR", "./runtime/audio"))
    logs_dir: Path = Path(os.getenv("LOGS_DIR", "./runtime/logs"))
    state_file: Path = Path(os.getenv("STATE_FILE", "./runtime/data/state.json"))

    def __post_init__(self):
        """Create necessary directories after initialization."""
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        """Validate settings."""
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")


# Singleton instance
settings = Settings()
