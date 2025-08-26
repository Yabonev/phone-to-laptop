"""Service for cleaning up temporary files."""

import logging
import os
from pathlib import Path
from typing import Optional


class CleanupService:
    """Handles cleanup of temporary files."""

    def __init__(self, audio_dir: str = "./runtime/audio"):
        """Initialize cleanup service."""
        self.logger = logging.getLogger(__name__)
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def cleanup_audio_file(self, file_path: Optional[Path]) -> None:
        """Clean up a temporary audio file."""
        if file_path and file_path.exists():
            try:
                os.remove(file_path)
                self.logger.info(f"Cleaned up audio file: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to clean up audio file {file_path}: {e}")

    def cleanup_old_files(self, max_age_hours: int = 24) -> None:
        """Clean up old temporary files."""
        import time
        current_time = time.time()
        
        for file_path in self.audio_dir.glob("*.ogg"):
            file_age_hours = (current_time - file_path.stat().st_mtime) / 3600
            if file_age_hours > max_age_hours:
                self.cleanup_audio_file(file_path)