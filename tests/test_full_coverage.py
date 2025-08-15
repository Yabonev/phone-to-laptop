"""Additional tests for maximum coverage"""
import pytest
import logging
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile

from src.commands.start import StartCommand
from src.commands.projects import ProjectsCommand
from src.commands.voice import VoiceMessageHandler
from src.core.bot import VoiceNotesBot
from src.services.transcription import TranscriptionService


class TestStartCommand:
    """Test start command"""
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_services):
        """Test start command execution"""
        command = StartCommand(mock_services)
        
        # Check properties
        assert command.name == "start"
        assert command.description == "Start the bot"
        assert command.menu_icon == ""  # StartCommand has no menu icon
        
        # Mock update and context
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        # Execute
        await command.execute(update, context)
        
        # Should send status message (start command shows status)
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "Voice Notes Bot" in call_args[0][0]


class TestProjectsCommandFull:
    """Test additional projects command functionality"""
    
    @pytest.mark.asyncio
    async def test_delete_confirmation_callback(self, mock_services):
        """Test project deletion confirmation"""
        mock_services['state'].get_projects.return_value = {"001": "Test Project"}
        command = ProjectsCommand(mock_services)
        
        # Setup delete confirmation callback
        query = Mock()
        query.data = "confirm_del_001"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        update = Mock()
        update.callback_query = query
        context = Mock()
        
        # Execute
        await command.handle_callback(update, context)
        
        # Should archive project
        mock_services['project'].archive_project.assert_called_once_with("001")
        
    @pytest.mark.asyncio
    async def test_delete_cancellation_callback(self, mock_services):
        """Test project deletion cancellation"""
        command = ProjectsCommand(mock_services)
        
        # Setup cancel callback
        query = Mock()
        query.data = "cancel_del"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        update = Mock()
        update.callback_query = query
        context = Mock()
        
        # Execute
        await command.handle_callback(update, context)
        
        # Should show cancellation message
        query.edit_message_text.assert_called_once()
        assert "cancelled" in query.edit_message_text.call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_delete_request_callback(self, mock_services):
        """Test project deletion request"""
        mock_services['state'].get_projects.return_value = {"001": "Test Project"}
        command = ProjectsCommand(mock_services)
        
        # Setup delete request
        query = Mock()
        query.data = "del_001"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        update = Mock()
        update.callback_query = query
        context = Mock()
        
        # Execute
        await command.handle_callback(update, context)
        
        # Should show confirmation dialog
        query.edit_message_text.assert_called_once()
        call_args = query.edit_message_text.call_args
        assert "Archive project" in call_args[0][0]
        assert "Test Project" in call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_invalid_project_selection(self, mock_services):
        """Test selecting non-existent project"""
        mock_services['state'].get_projects.return_value = {}
        command = ProjectsCommand(mock_services)
        
        query = Mock()
        query.data = "pick_999"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        update = Mock()
        update.callback_query = query
        context = Mock()
        
        await command.handle_callback(update, context)
        
        # Should show error
        query.edit_message_text.assert_called_once()
        assert "not found" in query.edit_message_text.call_args[0][0]


class TestVoiceHandlerFull:
    """Test additional voice handler functionality"""
    
    @pytest.mark.asyncio
    async def test_voice_with_project_not_found(self, mock_services):
        """Test voice when project exists in state but not on disk"""
        mock_services['state'].get_active_project.return_value = "001"
        mock_services['state'].get_projects.return_value = {}  # No projects
        mock_services['state'].is_message_processed.return_value = False
        
        handler = VoiceMessageHandler(mock_services)
        
        update = Mock()
        update.message = Mock()
        update.message.message_id = 123
        update.message.reply_text = AsyncMock()
        context = Mock()
        
        await handler.handle_voice(update, context)
        
        # Should show error
        update.message.reply_text.assert_called_once()
        assert "Project not found" in update.message.reply_text.call_args[0][0]
        
    @pytest.mark.asyncio
    async def test_voice_processing_success(self, mock_services, temp_dir):
        """Test successful voice processing"""
        # Setup mocks
        mock_services['state'].get_active_project.return_value = "001"
        mock_services['state'].get_projects.return_value = {"001": "Test Project"}
        mock_services['state'].is_message_processed.return_value = False
        mock_services['state'].get_language.return_value = "en"
        
        # Mock transcription
        mock_services['transcription'].create_temp_audio_file.return_value = temp_dir / "test.ogg"
        mock_services['transcription'].transcribe_audio = AsyncMock(
            return_value=("This is a test", "en")
        )
        mock_services['transcription'].cleanup_audio_file = Mock()
        
        # Mock project service
        mock_services['project'].add_note.return_value = True
        
        handler = VoiceMessageHandler(mock_services)
        
        # Create mock update
        voice_file = Mock()
        voice_file.get_file = AsyncMock()
        voice_file.get_file.return_value.download_to_drive = AsyncMock()
        
        update = Mock()
        update.message = Mock()
        update.message.message_id = 123
        update.message.voice = voice_file
        update.message.reply_text = AsyncMock()
        
        # Create mock processing message
        processing_msg = Mock()
        processing_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = processing_msg
        
        context = Mock()
        
        # Execute
        await handler.handle_voice(update, context)
        
        # Verify transcription happened
        mock_services['transcription'].transcribe_audio.assert_called_once()
        
        # Verify note was added
        mock_services['project'].add_note.assert_called_once_with(
            "001", "This is a test", None
        )
        
        # Verify message marked as processed
        mock_services['state'].mark_message_processed.assert_called_once_with("123")
        
    @pytest.mark.asyncio
    async def test_voice_with_bulgarian_translation(self, mock_services, temp_dir):
        """Test voice processing with Bulgarian translation"""
        mock_services['state'].get_active_project.return_value = "001"
        mock_services['state'].get_projects.return_value = {"001": "Test Project"}
        mock_services['state'].is_message_processed.return_value = False
        mock_services['state'].get_language.return_value = "bg"
        
        # Mock transcription
        audio_path = temp_dir / "test.ogg"
        audio_path.touch()
        mock_services['transcription'].create_temp_audio_file.return_value = audio_path
        mock_services['transcription'].transcribe_audio = AsyncMock(
            return_value=("Това е тест", "bg")
        )
        mock_services['transcription'].translate_to_english = AsyncMock(
            return_value="This is a test"
        )
        mock_services['transcription'].cleanup_audio_file = Mock()
        
        handler = VoiceMessageHandler(mock_services)
        
        # Create mock update
        voice_file = Mock()
        voice_file.get_file = AsyncMock()
        voice_file.get_file.return_value.download_to_drive = AsyncMock()
        
        update = Mock()
        update.message = Mock()
        update.message.message_id = 123
        update.message.voice = voice_file
        update.message.reply_text = AsyncMock()
        
        processing_msg = Mock()
        processing_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = processing_msg
        
        context = Mock()
        
        # Execute
        await handler.handle_voice(update, context)
        
        # Verify translation was called
        mock_services['transcription'].translate_to_english.assert_called_once()
        
        # Verify note added with translation
        mock_services['project'].add_note.assert_called_once_with(
            "001", "Това е тест", "This is a test"
        )
        
    @pytest.mark.asyncio
    async def test_voice_processing_error(self, mock_services):
        """Test voice processing with error"""
        mock_services['state'].get_active_project.return_value = "001"
        mock_services['state'].get_projects.return_value = {"001": "Test Project"}
        mock_services['state'].is_message_processed.return_value = False
        
        handler = VoiceMessageHandler(mock_services)
        
        # Mock voice file that fails
        voice_file = Mock()
        voice_file.get_file = AsyncMock(side_effect=Exception("Download failed"))
        
        update = Mock()
        update.message = Mock()
        update.message.message_id = 123
        update.message.voice = voice_file
        update.message.reply_text = AsyncMock()
        
        processing_msg = Mock()
        processing_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = processing_msg
        
        context = Mock()
        
        # Execute
        await handler.handle_voice(update, context)
        
        # Should show error message
        processing_msg.edit_text.assert_called_once()
        assert "Error" in processing_msg.edit_text.call_args[0][0]


class TestTranscriptionService:
    """Test transcription service"""
    
    def test_transcription_init(self, temp_dir):
        """Test transcription service initialization"""
        service = TranscriptionService(
            model_name="tiny",
            audio_dir=temp_dir / "audio"
        )
        
        assert service.model_name == "tiny"
        assert service.audio_dir == temp_dir / "audio"
        assert service.model is None  # Lazy loading
        assert service.audio_dir.exists()
        
    @patch('src.services.transcription.whisper.load_model')
    def test_lazy_model_loading(self, mock_load_model, temp_dir):
        """Test that model loads lazily"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        service = TranscriptionService("tiny", temp_dir / "audio")
        assert service.model is None
        
        # Trigger load
        service._load_model()
        assert service.model == mock_model
        mock_load_model.assert_called_once_with("tiny")
        
        # Second call shouldn't reload
        service._load_model()
        mock_load_model.assert_called_once()  # Still only once
        
    @pytest.mark.asyncio
    @patch('src.services.transcription.whisper.load_model')
    async def test_transcribe_audio(self, mock_load_model, temp_dir):
        """Test audio transcription"""
        # Setup mock model
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": " Test transcription ",
            "language": "en"
        }
        mock_load_model.return_value = mock_model
        
        service = TranscriptionService("tiny", temp_dir / "audio")
        
        # Create test audio file
        audio_file = temp_dir / "test.ogg"
        audio_file.touch()
        
        # Transcribe
        text, lang = await service.transcribe_audio(audio_file, "en")
        
        assert text == "Test transcription"  # Stripped
        assert lang == "en"
        mock_model.transcribe.assert_called_once()
        
    @pytest.mark.asyncio
    @patch('src.services.transcription.whisper.load_model')
    async def test_translate_to_english(self, mock_load_model, temp_dir):
        """Test translation to English"""
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": " English translation "
        }
        mock_load_model.return_value = mock_model
        
        service = TranscriptionService("tiny", temp_dir / "audio")
        
        audio_file = temp_dir / "test.ogg"
        audio_file.touch()
        
        # Translate
        translation = await service.translate_to_english(audio_file, "bg")
        
        assert translation == "English translation"
        # Check task parameter was set
        call_args = mock_model.transcribe.call_args
        assert call_args[1]["task"] == "translate"
        assert call_args[1]["language"] == "bg"
        
    def test_create_temp_audio_file(self, temp_dir):
        """Test temporary audio file creation"""
        service = TranscriptionService("tiny", temp_dir / "audio")
        
        temp_file = service.create_temp_audio_file(".ogg")
        
        assert temp_file.exists()
        assert temp_file.suffix == ".ogg"
        assert temp_file.parent == temp_dir / "audio"
        
        # Cleanup
        temp_file.unlink()
        
    def test_cleanup_audio_file(self, temp_dir):
        """Test audio file cleanup"""
        service = TranscriptionService("tiny", temp_dir / "audio")
        
        # Create test file
        test_file = temp_dir / "audio" / "test.ogg"
        test_file.touch()
        assert test_file.exists()
        
        # Cleanup
        service.cleanup_audio_file(test_file)
        assert not test_file.exists()
        
        # Cleanup non-existent file shouldn't error
        service.cleanup_audio_file(test_file)  # Should not raise


class TestBotQueueProcessing:
    """Test bot queue processing"""
    
    @pytest.mark.asyncio
    async def test_process_queued_voice_messages(self, test_config):
        """Test processing queued voice messages"""
        bot = VoiceNotesBot(test_config)
        
        # Register voice handler
        bot.register_command(VoiceMessageHandler)
        
        # Mock voice update
        voice_update = Mock()
        voice_update.update_id = 100
        voice_update.message = Mock()
        voice_update.message.voice = Mock()
        voice_update.message.text = None
        voice_update.callback_query = None
        
        # Mock application
        app = Mock()
        app.bot = Mock()
        app.bot.get_updates = AsyncMock(return_value=[voice_update])
        
        # Mock voice handler
        with patch.object(bot.registry.voice_handler, 'handle_voice', new_callable=AsyncMock):
            await bot.process_queued_messages(app)
            
            # Should process voice message
            bot.registry.voice_handler.handle_voice.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_process_queued_text_commands(self, test_config):
        """Test processing queued text commands"""
        bot = VoiceNotesBot(test_config)
        
        # Register start command
        from src.commands.start import StartCommand
        bot.register_command(StartCommand)
        
        # Mock text update
        text_update = Mock()
        text_update.update_id = 100
        text_update.message = Mock()
        text_update.message.voice = None
        text_update.message.text = "/start"
        text_update.callback_query = None
        
        # Mock application
        app = Mock()
        app.bot = Mock()
        app.bot.get_updates = AsyncMock(return_value=[text_update])
        
        # Mock command execution
        start_cmd = bot.registry.get_command("start")
        with patch.object(start_cmd, 'execute', new_callable=AsyncMock):
            await bot.process_queued_messages(app)
            
            # Should execute start command
            start_cmd.execute.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_process_queued_with_error(self, test_config):
        """Test queue processing with error"""
        bot = VoiceNotesBot(test_config)
        
        # Mock application with error
        app = Mock()
        app.bot = Mock()
        app.bot.get_updates = AsyncMock(side_effect=Exception("Network error"))
        
        # Should handle error gracefully
        await bot.process_queued_messages(app)
        # Should not raise


class TestCommandProperties:
    """Test command property coverage"""
    
    def test_command_properties(self):
        """Test all command properties"""
        from src.commands.start import StartCommand
        from src.commands.status import StatusCommand
        from src.commands.new_project import NewProjectCommand
        from src.commands.language import LanguageCommand
        
        # Start command
        start = StartCommand({})
        assert start.name == "start"
        assert start.description == "Start the bot"
        assert start.menu_icon == ""
        
        # Status command
        status = StatusCommand({})
        assert status.name == "status"
        assert status.description == "Show current status"
        assert status.menu_icon == "📊"
        
        # New project command
        new = NewProjectCommand({})
        assert new.name == "new"
        assert new.description == "Create new project"
        assert new.menu_icon == "➕"
        
        # Language command
        lang = LanguageCommand({})
        assert lang.name == "language"
        assert lang.description == "Change language"
        assert lang.menu_icon == "🌐"