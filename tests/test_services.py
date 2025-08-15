"""Tests for service layer components"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
import os
from unittest.mock import Mock

from src.services.container import ServiceContainer
from src.services.state import StateService
from src.services.project import ProjectService
from src.services.cleanup import CleanupService


class TestServiceContainer:
    """Test service container and dependency injection"""
    
    def test_container_initialization(self, test_config):
        """Test that all services are properly initialized"""
        container = ServiceContainer(test_config)
        
        # Check all required services exist
        assert container.get('state') is not None
        assert container.get('project') is not None
        assert container.get('transcription') is not None
        assert container.get('cleanup') is not None
        assert container.get('config') is not None
        
    def test_service_registration(self, test_config):
        """Test custom service registration"""
        container = ServiceContainer(test_config)
        
        # Register custom service
        custom_service = Mock()
        container.register('custom', custom_service)
        
        # Verify registration
        assert container.get('custom') == custom_service


class TestStateService:
    """Test state persistence and management"""
    
    def test_default_state(self, temp_dir):
        """Test initial state values"""
        state_file = temp_dir / "state.json"
        state = StateService(state_file)
        
        assert state.get_language() == "en"
        assert state.get_active_project() is None
        assert state.get_projects() == {}
        
    def test_project_management(self, temp_dir):
        """Test adding and managing projects"""
        state_file = temp_dir / "state.json"
        state = StateService(state_file)
        
        # Add project
        state.add_project("001", "Test Project")
        assert "001" in state.get_projects()
        assert state.get_projects()["001"] == "Test Project"
        
        # Set active project
        state.set_active_project("001")
        assert state.get_active_project() == "001"
        
    def test_language_setting(self, temp_dir):
        """Test language configuration"""
        state_file = temp_dir / "state.json"
        state = StateService(state_file)
        
        # Default should be English
        assert state.get_language() == "en"
        
        # Change to Bulgarian
        state.set_language("bg")
        assert state.get_language() == "bg"
        
    def test_message_tracking(self, temp_dir):
        """Test message processing tracking"""
        state_file = temp_dir / "state.json"
        state = StateService(state_file)
        
        # Mark messages as processed
        state.mark_message_processed("msg_1")
        state.mark_message_processed("msg_2")
        
        assert state.is_message_processed("msg_1")
        assert state.is_message_processed("msg_2")
        assert not state.is_message_processed("msg_3")
        
    def test_state_persistence(self, temp_dir):
        """Test that state persists to disk"""
        state_file = temp_dir / "state.json"
        
        # Create and modify state
        state1 = StateService(state_file)
        state1.add_project("001", "Test")
        state1.set_language("bg")
        state1.set_active_project("001")
        
        # Load in new instance
        state2 = StateService(state_file)
        assert state2.get_projects()["001"] == "Test"
        assert state2.get_language() == "bg"
        assert state2.get_active_project() == "001"


class TestProjectService:
    """Test project file management"""
    
    def test_project_creation(self, temp_dir):
        """Test creating a new project"""
        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)
        
        # Create first project
        project_id = service.create_project("My Project", {})
        assert project_id == "001"
        
        # Verify directory structure
        project_dir = service.get_project_dir("001")
        assert project_dir.exists()
        assert project_dir.name.startswith("project-001-")
        
        # Verify notes file
        notes_file = project_dir / "notes.md"
        assert notes_file.exists()
        content = notes_file.read_text()
        assert "# My Project" in content
        
    def test_sequential_ids(self, temp_dir):
        """Test that project IDs increment correctly"""
        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)
        
        # Create multiple projects
        id1 = service.create_project("Project 1", {})
        id2 = service.create_project("Project 2", {"001": "Project 1"})
        id3 = service.create_project("Project 3", {"001": "Project 1", "002": "Project 2"})
        
        assert id1 == "001"
        assert id2 == "002"
        assert id3 == "003"
        
    def test_add_notes(self, temp_dir):
        """Test adding notes to a project"""
        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)
        
        # Create project and add notes
        project_id = service.create_project("Test", {})
        success = service.add_note(project_id, "This is a test note", None)
        assert success
        
        # Verify note was added
        notes_file = service.get_project_dir(project_id) / "notes.md"
        content = notes_file.read_text()
        assert "This is a test note" in content
        
    def test_add_notes_with_translation(self, temp_dir):
        """Test adding Bulgarian notes with English translation"""
        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)
        
        # Create project and add translated note
        project_id = service.create_project("Test", {})
        success = service.add_note(
            project_id, 
            "Това е тест", 
            "This is a test"
        )
        assert success
        
        # Verify both languages present
        notes_file = service.get_project_dir(project_id) / "notes.md"
        content = notes_file.read_text()
        assert "**Bulgarian:** Това е тест" in content
        assert "**English:** This is a test" in content
        
    def test_project_stats(self, temp_dir):
        """Test getting project statistics"""
        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)
        
        # Create project and add notes
        project_id = service.create_project("Test", {})
        service.add_note(project_id, "First note with some words")
        service.add_note(project_id, "Second note with more words here")
        
        # Get stats
        messages, words = service.get_project_stats(project_id)
        assert messages == 2
        assert words > 0  # Should count all words
        
    def test_project_archival(self, temp_dir):
        """Test archiving projects"""
        projects_dir = temp_dir / "projects"
        service = ProjectService(projects_dir)
        
        # Create and archive project
        project_id = service.create_project("To Archive", {})
        project_dir = service.get_project_dir(project_id)
        
        # Archive it
        success = service.archive_project(project_id)
        assert success
        assert not project_dir.exists()
        
        # Check archive exists
        archive_dir = temp_dir / "archive"
        assert archive_dir.exists()
        archived = list(archive_dir.glob("project-001-*"))
        assert len(archived) == 1


class TestCleanupService:
    """Test cleanup and maintenance functionality"""
    
    def test_old_audio_cleanup(self, temp_dir):
        """Test deletion of old audio files"""
        audio_dir = temp_dir / "audio"
        audio_dir.mkdir()
        
        # Create old and new files
        old_file = audio_dir / "old.ogg"
        new_file = audio_dir / "new.ogg"
        old_file.touch()
        new_file.touch()
        
        # Make old file 8 days old
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(old_file, (old_time, old_time))
        
        # Run cleanup
        cleanup = CleanupService(audio_dir, temp_dir / "logs")
        deleted_count = cleanup.cleanup_old_audio_files()
        
        assert deleted_count == 1
        assert not old_file.exists()
        assert new_file.exists()
        
    def test_audio_cleanup_retention(self, temp_dir):
        """Test that recent files are kept"""
        audio_dir = temp_dir / "audio"
        audio_dir.mkdir()
        
        # Create files of various ages
        for days_old in [1, 3, 5, 6, 7, 8, 10]:
            file = audio_dir / f"file_{days_old}d.ogg"
            file.touch()
            file_time = (datetime.now() - timedelta(days=days_old)).timestamp()
            os.utime(file, (file_time, file_time))
        
        # Run cleanup (7 day retention)
        cleanup = CleanupService(audio_dir, temp_dir / "logs")
        deleted_count = cleanup.cleanup_old_audio_files()
        
        # Files 7, 8 and 10 days old should be deleted (>= 7 days)
        assert deleted_count == 3
        assert not (audio_dir / "file_8d.ogg").exists()
        assert not (audio_dir / "file_10d.ogg").exists()
        
        # Files less than 7 days should exist
        for days in [1, 3, 5, 6]:
            assert (audio_dir / f"file_{days}d.ogg").exists()
        # 7 day old file should be deleted
        assert not (audio_dir / "file_7d.ogg").exists()
            
    def test_log_rotation(self, temp_dir):
        """Test log file rotation"""
        logs_dir = temp_dir / "logs"
        logs_dir.mkdir()
        log_file = logs_dir / "bot.log"
        
        # Create large log file
        with open(log_file, "w") as f:
            for i in range(1500):
                f.write(f"Line {i}\n")
        
        # Run rotation
        cleanup = CleanupService(temp_dir / "audio", logs_dir)
        rotated = cleanup.rotate_log_file("bot.log")
        
        assert rotated is True
        
        # Check file was truncated
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1000
            # Should keep last 1000 lines (500-1499)
            assert lines[0].strip() == "Line 500"
            assert lines[-1].strip() == "Line 1499"
            
    def test_log_rotation_small_file(self, temp_dir):
        """Test that small logs are not rotated"""
        logs_dir = temp_dir / "logs"
        logs_dir.mkdir()
        log_file = logs_dir / "bot.log"
        
        # Create small log file
        with open(log_file, "w") as f:
            for i in range(500):
                f.write(f"Line {i}\n")
        
        # Run rotation
        cleanup = CleanupService(temp_dir / "audio", logs_dir)
        rotated = cleanup.rotate_log_file("bot.log")
        
        assert rotated is False
        
        # Check file unchanged
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 500
            
    def test_full_cleanup_run(self, temp_dir):
        """Test running all cleanup tasks"""
        audio_dir = temp_dir / "audio"
        logs_dir = temp_dir / "logs"
        audio_dir.mkdir()
        logs_dir.mkdir()
        
        # Create old audio file
        old_audio = audio_dir / "old.ogg"
        old_audio.touch()
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(old_audio, (old_time, old_time))
        
        # Create large log
        log_file = logs_dir / "bot.log"
        with open(log_file, "w") as f:
            for i in range(1200):
                f.write(f"Line {i}\n")
        
        # Run full cleanup
        cleanup = CleanupService(audio_dir, logs_dir)
        cleanup.run_cleanup()
        
        # Verify results
        assert not old_audio.exists()
        with open(log_file, "r") as f:
            assert len(f.readlines()) == 1000