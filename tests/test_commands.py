"""Tests for bot commands"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from src.commands.language import LanguageCommand
from src.commands.status import StatusCommand
from src.commands.new_project import NewProjectCommand
from src.commands.projects import ProjectsCommand
from src.commands.voice import VoiceMessageHandler


class TestLanguageCommand:
    """Test language selection command"""
    
    @pytest.mark.asyncio
    async def test_language_command_buttons(self):
        """Test language command shows correct buttons"""
        services = {
            'state': Mock(),
            'project': Mock(),
            'transcription': Mock(),
            'config': {}
        }
        services['state'].get_language.return_value = "en"
        
        command = LanguageCommand(services)
        
        # Mock update and context
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        # Execute command
        await command.execute(update, context)
        
        # Verify reply was sent with buttons
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        
        # Check message content
        assert "Select transcription language" in call_args[0][0]
        
        # Check keyboard exists
        assert 'reply_markup' in call_args[1]
        
    @pytest.mark.asyncio
    async def test_language_callback_handler(self, mock_services):
        """Test language selection via callback"""
        services = mock_services
        
        command = LanguageCommand(services)
        
        # Mock callback query
        query = Mock()
        query.data = "lang_bg"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        update = Mock()
        update.callback_query = query
        context = Mock()
        
        # Handle callback
        await command.handle_callback(update, context)
        
        # Verify language was set
        services['state'].set_language.assert_called_once_with("bg")
        
        # Verify response
        query.answer.assert_called_once()
        query.edit_message_text.assert_called_once()
        assert "Bulgarian" in query.edit_message_text.call_args[0][0]


class TestStatusCommand:
    """Test status command"""
    
    @pytest.mark.asyncio
    async def test_status_no_project(self):
        """Test status when no project selected"""
        services = {
            'state': Mock(),
            'project': Mock(),
            'transcription': Mock(),
            'config': {}
        }
        services['state'].get_active_project.return_value = None
        
        command = StatusCommand(services)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await command.execute(update, context)
        
        # Should show no project message
        update.message.reply_text.assert_called_once()
        assert "No active project" in update.message.reply_text.call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_status_with_project(self, mock_services):
        """Test status with active project"""
        services = mock_services
        services['state'].get_active_project.return_value = "001"
        services['state'].get_projects.return_value = {"001": "My Project"}
        services['state'].get_language.return_value = "en"
        services['project'].get_project_stats.return_value = (5, 100)
        
        command = StatusCommand(services)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await command.execute(update, context)
        
        # Should show project stats
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        assert "My Project" in message
        assert "Messages: 5" in message
        assert "Total words: 100" in message
        assert "English" in message


class TestNewProjectCommand:
    """Test new project creation command"""
    
    @pytest.mark.asyncio
    async def test_create_project_no_name(self):
        """Test creating project without name"""
        services = {
            'state': Mock(),
            'project': Mock(),
            'transcription': Mock(),
            'config': {}
        }
        
        command = NewProjectCommand(services)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = []  # No args
        
        await command.execute(update, context)
        
        # Should show usage message
        update.message.reply_text.assert_called_once()
        assert "Usage:" in update.message.reply_text.call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_create_project_with_name(self, mock_services):
        """Test creating project with name"""
        services = mock_services
        services['state'].get_projects.return_value = {}
        services['project'].create_project.return_value = "001"
        
        command = NewProjectCommand(services)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ["My", "Test", "Project"]
        
        await command.execute(update, context)
        
        # Verify project created
        services['project'].create_project.assert_called_once_with(
            "My Test Project",
            {}
        )
        
        # Verify state updated
        services['state'].add_project.assert_called_once_with("001", "My Test Project")
        
        # Verify success message
        update.message.reply_text.assert_called_once()
        message = update.message.reply_text.call_args[0][0]
        assert "Created project" in message
        assert "My Test Project" in message


class TestProjectsCommand:
    """Test projects listing command"""
    
    @pytest.mark.asyncio
    async def test_list_no_projects(self):
        """Test listing when no projects"""
        services = {
            'state': Mock(),
            'project': Mock(),
            'transcription': Mock(),
            'config': {}
        }
        services['state'].get_projects.return_value = {}
        
        command = ProjectsCommand(services)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await command.execute(update, context)
        
        # Should show no projects message
        update.message.reply_text.assert_called_once()
        assert "No projects yet" in update.message.reply_text.call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_list_with_projects(self):
        """Test listing projects with buttons"""
        services = {
            'state': Mock(),
            'project': Mock(),
            'transcription': Mock(),
            'config': {}
        }
        services['state'].get_projects.return_value = {
            "001": "Project 1",
            "002": "Project 2"
        }
        
        command = ProjectsCommand(services)
        
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await command.execute(update, context)
        
        # Should show projects with keyboard
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        
        assert "Select or archive a project" in call_args[0][0]
        assert 'reply_markup' in call_args[1]
        
    @pytest.mark.asyncio
    async def test_project_selection_callback(self, mock_services):
        """Test selecting project via button"""
        services = mock_services
        services['state'].get_projects.return_value = {"001": "My Project"}
        
        command = ProjectsCommand(services)
        
        query = Mock()
        query.data = "pick_001"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        update = Mock()
        update.callback_query = query
        context = Mock()
        
        await command.handle_callback(update, context)
        
        # Verify project was selected
        services['state'].set_active_project.assert_called_once_with("001")
        
        # Verify response
        query.answer.assert_called_once()
        query.edit_message_text.assert_called_once()
        assert "Selected project" in query.edit_message_text.call_args[0][0]


class TestVoiceMessageHandler:
    """Test voice message processing"""
    
    @pytest.mark.asyncio
    async def test_voice_no_project(self):
        """Test voice message without active project"""
        services = {
            'state': Mock(),
            'project': Mock(),
            'transcription': Mock(),
            'config': {}
        }
        services['state'].get_active_project.return_value = None
        services['state'].is_message_processed.return_value = False
        
        handler = VoiceMessageHandler(services)
        
        update = Mock()
        update.message = Mock()
        update.message.message_id = 123
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await handler.handle_voice(update, context)
        
        # Should show no project error
        update.message.reply_text.assert_called_once()
        assert "No project selected" in update.message.reply_text.call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_voice_already_processed(self, mock_services):
        """Test handling already processed message"""
        services = mock_services
        services['state'].is_message_processed.return_value = True
        
        handler = VoiceMessageHandler(services)
        
        update = Mock()
        update.message = Mock()
        update.message.message_id = 123
        context = Mock()
        
        await handler.handle_voice(update, context)
        
        # Should skip processing
        services['transcription'].transcribe_audio.assert_not_called()