"""
Project management service - Single Responsibility
"""
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict


class ProjectService:
    """Manages project files and directories"""
    
    def __init__(self, projects_dir: Path = Path("./projects")):
        self.projects_dir = projects_dir
        self.projects_dir.mkdir(exist_ok=True)
    
    def create_project(self, project_name: str, existing_projects: Dict[str, str]) -> str:
        """Create a new project and return its ID"""
        # Sanitize name for filesystem
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Generate project ID
        if existing_projects:
            max_id = max(int(pid) for pid in existing_projects.keys())
            project_id = str(max_id + 1).zfill(3)
        else:
            project_id = "001"
        
        # Create project directory
        project_dir = self.projects_dir / f"project-{project_id}-{safe_name.replace(' ', '-').lower()}"
        project_dir.mkdir(exist_ok=True)
        
        # Create notes file
        notes_file = project_dir / "notes.md"
        notes_file.write_text(f"# {project_name}\n\nVoice notes transcriptions:\n\n")
        
        return project_id
    
    def archive_project(self, project_id: str) -> bool:
        """Archive a project by moving to archive folder with timestamp"""
        # Create archive directory if it doesn't exist
        archive_dir = self.projects_dir.parent / "archive"
        archive_dir.mkdir(exist_ok=True)
        
        for dir_path in self.projects_dir.iterdir():
            if dir_path.name.startswith(f"project-{project_id}-"):
                # Add timestamp to folder name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archived_name = f"{dir_path.name}_archived_{timestamp}"
                archive_path = archive_dir / archived_name
                
                # Move to archive
                shutil.move(str(dir_path), str(archive_path))
                return True
        return False
    
    def get_project_dir(self, project_id: str) -> Optional[Path]:
        """Get project directory path"""
        for dir_path in self.projects_dir.iterdir():
            if dir_path.name.startswith(f"project-{project_id}-"):
                return dir_path
        return None
    
    def add_note(self, project_id: str, text: str, translation: Optional[str] = None) -> bool:
        """Add a voice note to project"""
        project_dir = self.get_project_dir(project_id)
        if not project_dir:
            return False
        
        notes_file = project_dir / "notes.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(notes_file, 'a') as f:
            if translation:
                f.write(f"## {timestamp} [VOICE]\n\n**Bulgarian:** {text}\n\n**English:** {translation}\n\n")
            else:
                f.write(f"## {timestamp} [VOICE]\n\n{text}\n\n")
        
        return True
    
    def add_text_note(self, project_id: str, text: str) -> bool:
        """Add a text note to project"""
        project_dir = self.get_project_dir(project_id)
        if not project_dir:
            return False
        
        notes_file = project_dir / "notes.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(notes_file, 'a') as f:
            f.write(f"## {timestamp} [TEXT]\n\n{text}\n\n")
        
        return True
    
    def get_project_stats(self, project_id: str) -> Tuple[int, int]:
        """Get message count and total words for a project"""
        project_dir = self.get_project_dir(project_id)
        if not project_dir:
            return 0, 0
        
        notes_file = project_dir / "notes.md"
        if not notes_file.exists():
            return 0, 0
        
        content = notes_file.read_text()
        
        # Count messages (each has ## timestamp)
        message_count = content.count("\n## ")
        
        # Count words
        total_words = 0
        lines = content.split('\n')
        for line in lines:
            if line and not line.startswith('#'):
                total_words += len(line.split())
        
        return message_count, total_words