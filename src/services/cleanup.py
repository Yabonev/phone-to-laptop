"""
Cleanup service - Manages old files and log rotation
"""
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


class CleanupService:
    """Handles cleanup of old audio files and log rotation"""
    
    def __init__(self, audio_dir: Path = Path("./audio"), logs_dir: Path = Path("./logs")):
        self.audio_dir = audio_dir
        self.logs_dir = logs_dir
        self.logger = logging.getLogger(__name__)
        self.max_log_lines = 1000
        self.audio_retention_days = 7
    
    def cleanup_old_audio_files(self) -> int:
        """Delete audio files older than retention period"""
        if not self.audio_dir.exists():
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now() - timedelta(days=self.audio_retention_days)
        
        for audio_file in self.audio_dir.glob("*.ogg"):
            try:
                # Get file modification time
                file_mtime = datetime.fromtimestamp(audio_file.stat().st_mtime)
                
                # Delete if older than retention period
                if file_mtime < cutoff_time:
                    audio_file.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old audio file: {audio_file.name}")
            except Exception as e:
                self.logger.error(f"Error deleting audio file {audio_file}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old audio files")
        
        return deleted_count
    
    def rotate_log_file(self, log_file: str = "bot.log") -> bool:
        """Rotate log file if it exceeds max lines"""
        log_path = self.logs_dir / log_file
        
        if not log_path.exists():
            return False
        
        try:
            # Read all lines
            with open(log_path, 'r') as f:
                lines = f.readlines()
            
            # Check if rotation needed
            if len(lines) <= self.max_log_lines:
                return False
            
            # Keep only the most recent lines
            lines_to_keep = lines[-self.max_log_lines:]
            
            # Write back the truncated log
            with open(log_path, 'w') as f:
                f.writelines(lines_to_keep)
            
            self.logger.info(f"Rotated log file {log_file}: kept last {self.max_log_lines} lines")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rotating log file {log_file}: {e}")
            return False
    
    def run_cleanup(self) -> None:
        """Run all cleanup tasks"""
        self.logger.info("Running cleanup tasks...")
        
        # Clean old audio files
        audio_deleted = self.cleanup_old_audio_files()
        
        # Rotate log files
        log_rotated = self.rotate_log_file("bot.log")
        
        # Also rotate launchd logs if they exist
        self.rotate_log_file("launchd.out.log")
        self.rotate_log_file("launchd.err.log")
        
        self.logger.info(f"Cleanup complete. Audio files deleted: {audio_deleted}, Log rotated: {log_rotated}")