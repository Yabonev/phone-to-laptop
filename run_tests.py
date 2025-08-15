#!/usr/bin/env python3
"""
Automated test runner for Phone-to-Laptop Bot
Can be executed by any LLM with: uv run python run_tests.py
"""

import sys
import traceback
from pathlib import Path
import shutil
import json
from datetime import datetime, timedelta
import os

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def run_test(self, name, test_func):
        """Run a single test and track results"""
        print(f"\n{BLUE}📝 Testing: {name}{RESET}")
        try:
            test_func()
            print(f"{GREEN}✅ PASSED: {name}{RESET}")
            self.passed += 1
            self.tests.append((name, True, None))
        except Exception as e:
            print(f"{RED}❌ FAILED: {name}{RESET}")
            print(f"{RED}   Error: {str(e)}{RESET}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
            if '--verbose' in sys.argv:
                traceback.print_exc()
    
    def test_service_initialization(self):
        """Test that all services can be initialized"""
        from src.services.container import ServiceContainer
        
        config = {
            'state_file': 'test_state.json',
            'projects_dir': './test_projects',
            'audio_dir': './test_audio',
            'logs_dir': './test_logs',
            'whisper_model': 'tiny'
        }
        
        container = ServiceContainer(config)
        
        # Check all services exist
        required_services = ['state', 'project', 'transcription', 'cleanup', 'config']
        for service_name in required_services:
            service = container.get(service_name)
            assert service is not None, f"Service {service_name} not found"
        
        # Cleanup
        Path('test_state.json').unlink(missing_ok=True)
    
    def test_state_persistence(self):
        """Test state saving and loading"""
        from src.services.state import StateService
        
        test_file = Path("test_state.json")
        
        # Create and modify state
        state = StateService(test_file)
        state.add_project("001", "Test Project")
        state.set_active_project("001")
        state.set_language("bg")
        state.mark_message_processed("msg_123")
        
        # Verify saved data
        with open(test_file, "r") as f:
            saved = json.load(f)
            assert saved["active_project"] == "001"
            assert saved["language"] == "bg"
            assert "001" in saved["projects"]
            assert "msg_123" in saved["processed_messages"]
        
        # Test loading
        state2 = StateService(test_file)
        assert state2.get_active_project() == "001"
        assert state2.get_language() == "bg"
        
        # Cleanup
        test_file.unlink()
    
    def test_project_management(self):
        """Test project creation and management"""
        from src.services.project import ProjectService
        
        projects_dir = Path("./test_projects")
        service = ProjectService(projects_dir)
        
        # Create project
        project_id = service.create_project("Test Project", {})
        assert project_id == "001"
        
        # Add note
        success = service.add_note("001", "Test note", "Test translation")
        assert success
        
        # Check files
        project_dir = service.get_project_dir("001")
        assert project_dir.exists()
        notes_file = project_dir / "notes.md"
        assert notes_file.exists()
        
        # Get stats
        messages, words = service.get_project_stats("001")
        assert messages > 0
        assert words > 0
        
        # Archive
        archived = service.archive_project("001")
        assert archived
        assert not project_dir.exists()
        
        # Cleanup
        shutil.rmtree(projects_dir.parent / "archive", ignore_errors=True)
        shutil.rmtree(projects_dir, ignore_errors=True)
    
    def test_language_settings(self):
        """Test language configuration"""
        from src.services.state import StateService
        
        test_file = Path("test_state.json")
        state = StateService(test_file)
        
        # Test default
        assert state.get_language() == "en"
        
        # Test setting
        state.set_language("bg")
        assert state.get_language() == "bg"
        
        # Test persistence
        state2 = StateService(test_file)
        assert state2.get_language() == "bg"
        
        # Cleanup
        test_file.unlink()
    
    def test_cleanup_service(self):
        """Test cleanup functionality"""
        from src.services.cleanup import CleanupService
        
        # Setup
        audio_dir = Path("./test_audio")
        logs_dir = Path("./test_logs")
        audio_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)
        
        cleanup = CleanupService(audio_dir, logs_dir)
        
        # Test audio cleanup
        old_file = audio_dir / "old.ogg"
        new_file = audio_dir / "new.ogg"
        old_file.touch()
        new_file.touch()
        
        # Make old file 8 days old
        old_time = (datetime.now() - timedelta(days=8)).timestamp()
        os.utime(old_file, (old_time, old_time))
        
        deleted = cleanup.cleanup_old_audio_files()
        assert deleted == 1
        assert not old_file.exists()
        assert new_file.exists()
        
        # Test log rotation
        log_file = logs_dir / "bot.log"
        with open(log_file, "w") as f:
            for i in range(1500):
                f.write(f"Line {i}\n")
        
        rotated = cleanup.rotate_log_file("bot.log")
        assert rotated
        
        with open(log_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1000
        
        # Cleanup
        shutil.rmtree(audio_dir)
        shutil.rmtree(logs_dir)
    
    def test_command_registration(self):
        """Test command registration system"""
        from src.core.registry import CommandRegistry
        from src.core.command import Command
        
        class TestCommand(Command):
            @property
            def name(self):
                return "test"
            
            @property
            def description(self):
                return "Test command"
            
            async def execute(self, update, context):
                pass
        
        registry = CommandRegistry()
        test_cmd = TestCommand({})  # Initialize command with empty services
        registry.register(test_cmd)
        
        # Check command is registered
        assert "test" in registry.commands
        cmd = registry.get_command("test")
        assert cmd is not None
        assert isinstance(cmd, TestCommand)
    
    def test_bot_initialization(self):
        """Test bot can be initialized"""
        from src.core.bot import VoiceNotesBot
        
        config = {
            'telegram_token': 'test_token',
            'whisper_model': 'tiny',
            'projects_dir': './test_projects',
            'audio_dir': './test_audio',
            'logs_dir': './test_logs',
            'state_file': 'test_state.json'
        }
        
        bot = VoiceNotesBot(config)
        
        # Check services
        assert bot.container.get('state') is not None
        assert bot.container.get('project') is not None
        assert bot.container.get('cleanup') is not None
        
        # Check directories
        assert Path('./test_projects').exists()
        assert Path('./test_audio').exists()
        assert Path('./test_logs').exists()
        
        # Cleanup
        shutil.rmtree('./test_projects', ignore_errors=True)
        shutil.rmtree('./test_audio', ignore_errors=True)
        shutil.rmtree('./test_logs', ignore_errors=True)
        Path('test_state.json').unlink(missing_ok=True)
    
    def run_all(self):
        """Run all tests"""
        print(f"{YELLOW}{'='*50}")
        print(f"Phone-to-Laptop Bot Test Suite")
        print(f"{'='*50}{RESET}")
        
        # Run each test
        self.run_test("Service Initialization", self.test_service_initialization)
        self.run_test("State Persistence", self.test_state_persistence)
        self.run_test("Project Management", self.test_project_management)
        self.run_test("Language Settings", self.test_language_settings)
        self.run_test("Cleanup Service", self.test_cleanup_service)
        self.run_test("Command Registration", self.test_command_registration)
        self.run_test("Bot Initialization", self.test_bot_initialization)
        
        # Print summary
        print(f"\n{YELLOW}{'='*50}")
        print(f"Test Results Summary")
        print(f"{'='*50}{RESET}")
        print(f"{GREEN}✅ Passed: {self.passed}{RESET}")
        print(f"{RED}❌ Failed: {self.failed}{RESET}")
        
        # Detailed results
        if '--verbose' in sys.argv or self.failed > 0:
            print(f"\n{YELLOW}Detailed Results:{RESET}")
            for name, passed, error in self.tests:
                if passed:
                    print(f"  {GREEN}✓{RESET} {name}")
                else:
                    print(f"  {RED}✗{RESET} {name}")
                    if error:
                        print(f"    {RED}→ {error}{RESET}")
        
        print(f"\n{YELLOW}{'='*50}{RESET}")
        
        # Return exit code
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    runner = TestRunner()
    sys.exit(runner.run_all())