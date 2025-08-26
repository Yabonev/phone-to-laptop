"""
REAL command tests using actual services instead of mocks

These tests validate actual command functionality by using real services
and verifying actual state changes, file operations, and workflows.
"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.commands.language import LanguageCommand
from src.bot.commands.new_project import NewProjectCommand
from src.bot.commands.projects import ProjectsCommand
from src.bot.commands.status import StatusCommand
from src.bot.handlers.voice import VoiceMessageHandler
from src.core.services.container import ServiceContainer


class TestStatusCommandReal:
    """Test status command with real services"""

    @pytest.mark.integration
    def test_status_command_with_real_services(self, real_services):
        """Test status command using real service container"""
        command = StatusCommand(real_services.get_all())

        # Verify command properties
        assert command.name == "status"
        assert command.description == "Show current status"
        assert command.menu_icon == "📊"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_status_no_project_with_real_state(self, real_services):
        """Test status when no project is selected using real state service"""
        services = real_services.get_all()
        command = StatusCommand(services)

        # Use real state service - should have no active project initially
        assert services["state"].get_active_project() is None

        # Mock Telegram update/context
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()

        # Execute command
        await command.execute(update, context)

        # Verify response
        update.message.reply_text.assert_called_once()
        message_text = update.message.reply_text.call_args[0][0]
        assert "No active project" in message_text

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_status_with_real_project(self, real_services):
        """Test status with a real project created through services"""
        services = real_services.get_all()

        # Create a real project using project service
        project_id = services["project"].create_project("Integration Test Project", {})

        # Add the project to state
        services["state"].add_project(project_id, "Integration Test Project")
        services["state"].set_active_project(project_id)

        # Add a real note to the project
        services["project"].add_note(project_id, "This is a test note for integration testing")

        # Create command
        command = StatusCommand(services)

        # Mock Telegram update/context
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()

        # Execute command
        await command.execute(update, context)

        # Verify response includes real project data
        update.message.reply_text.assert_called_once()
        message_text = update.message.reply_text.call_args[0][0]

        assert "Integration Test Project" in message_text
        assert "Messages: 1" in message_text
        assert "Total words:" in message_text
        assert "English" in message_text  # Default language

        # Verify the project file actually exists
        project_dir = services["project"].get_project_dir(project_id)
        assert project_dir.exists()
        notes_file = project_dir / "notes.md"
        assert notes_file.exists()

        # Verify note content
        notes_content = notes_file.read_text()
        assert "Integration Test Project" in notes_content
        assert "This is a test note for integration testing" in notes_content


class TestNewProjectCommandReal:
    """Test new project command with real services"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_project_real_workflow(self, real_services):
        """Test complete project creation workflow with real services"""
        services = real_services.get_all()
        command = NewProjectCommand(services)

        # Mock Telegram update/context with project name
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ["Real", "Integration", "Project"]

        # Get initial project count
        initial_projects = services["state"].get_projects()
        initial_count = len(initial_projects)

        # Execute command
        await command.execute(update, context)

        # Verify success response
        update.message.reply_text.assert_called_once()
        message_text = update.message.reply_text.call_args[0][0]
        assert "Created project" in message_text
        assert "Real Integration Project" in message_text

        # Verify project was actually created in state
        projects = services["state"].get_projects()
        assert len(projects) == initial_count + 1

        # Find the new project
        new_project_id = None
        for pid, name in projects.items():
            if name == "Real Integration Project":
                new_project_id = pid
                break

        assert new_project_id is not None

        # Verify project directory and files exist
        project_dir = services["project"].get_project_dir(new_project_id)
        assert project_dir.exists()
        assert project_dir.name.startswith(f"project-{new_project_id}-")

        notes_file = project_dir / "notes.md"
        assert notes_file.exists()

        # Verify notes file content
        notes_content = notes_file.read_text()
        assert "# Real Integration Project" in notes_content
        assert "Voice notes transcriptions:" in notes_content

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_project_no_args_error(self, real_services):
        """Test project creation error handling with real services"""
        services = real_services.get_all()
        command = NewProjectCommand(services)

        # Mock Telegram update/context without args
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = []  # No project name

        # Execute command
        await command.execute(update, context)

        # Verify error response
        update.message.reply_text.assert_called_once()
        message_text = update.message.reply_text.call_args[0][0]
        assert "Usage:" in message_text


class TestLanguageCommandReal:
    """Test language command with real state management"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_language_change_real_state(self, real_services):
        """Test language change with real state persistence"""
        services = real_services.get_all()
        command = LanguageCommand(services)

        # Verify initial language
        assert services["state"].get_language() == "en"

        # Mock callback query for Bulgarian
        query = Mock()
        query.data = "lang_bg"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = Mock()
        update.callback_query = query
        context = Mock()

        # Execute callback
        await command.handle_callback(update, context)

        # Verify language was actually changed in state
        assert services["state"].get_language() == "bg"

        # Verify response
        query.answer.assert_called_once()
        query.edit_message_text.assert_called_once()

        # Verify state persistence by creating new service container
        services["config"]["state_file"]
        new_container = ServiceContainer(services["config"])
        assert new_container.get("state").get_language() == "bg"


class TestProjectsCommandReal:
    """Test projects command with real project management"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_project_selection_real_workflow(self, real_services):
        """Test project selection with real services"""
        services = real_services.get_all()

        # Create real projects
        project1_id = services["project"].create_project("Project Alpha", {})
        project2_id = services["project"].create_project("Project Beta", {"001": "Project Alpha"})

        services["state"].add_project(project1_id, "Project Alpha")
        services["state"].add_project(project2_id, "Project Beta")

        command = ProjectsCommand(services)

        # Mock callback for selecting project 2
        query = Mock()
        query.data = f"pick_{project2_id}"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = Mock()
        update.callback_query = query
        context = Mock()

        # Execute selection
        await command.handle_callback(update, context)

        # Verify project was actually selected
        assert services["state"].get_active_project() == project2_id

        # Verify response
        query.edit_message_text.assert_called_once()
        response_text = query.edit_message_text.call_args[0][0]
        assert "Selected project" in response_text
        assert "Project Beta" in response_text

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_project_archival_real_filesystem(self, real_services):
        """Test project archival with real file operations"""
        services = real_services.get_all()

        # Create and populate a real project
        project_id = services["project"].create_project("Project to Archive", {})
        services["state"].add_project(project_id, "Project to Archive")

        # Add some content
        services["project"].add_note(project_id, "This project will be archived")

        # Verify project exists
        project_dir = services["project"].get_project_dir(project_id)
        assert project_dir.exists()

        command = ProjectsCommand(services)

        # Mock archival confirmation callback
        query = Mock()
        query.data = f"confirm_del_{project_id}"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update = Mock()
        update.callback_query = query
        context = Mock()

        # Execute archival
        await command.handle_callback(update, context)

        # Verify project directory was actually moved/deleted
        assert not project_dir.exists()

        # Verify archive directory exists
        projects_dir = Path(services["config"]["projects_dir"])
        archive_dir = projects_dir.parent / "archive"
        assert archive_dir.exists()

        # Verify project was archived
        archived_projects = list(archive_dir.glob(f"project-{project_id}-*"))
        assert len(archived_projects) == 1


class TestVoiceMessageHandlerReal:
    """Test voice message handling with real services (mocked Telegram API only)"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_voice_processing_real_workflow_no_audio(self, real_services):
        """Test voice message processing workflow without actual audio transcription"""
        services = real_services.get_all()

        # Create real project first
        project_id = services["project"].create_project("Voice Test Project", {})
        services["state"].add_project(project_id, "Voice Test Project")
        services["state"].set_active_project(project_id)

        handler = VoiceMessageHandler(services)

        # Mock Telegram voice message (but skip actual audio processing)
        voice_file = Mock()
        voice_file.get_file = AsyncMock()
        mock_file = Mock()
        mock_file.download_to_drive = AsyncMock()
        voice_file.get_file.return_value = mock_file

        update = Mock()
        update.message = Mock()
        update.message.message_id = 12345
        update.message.voice = voice_file
        update.message.reply_text = AsyncMock()

        processing_msg = Mock()
        processing_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = processing_msg

        context = Mock()

        # Mock transcription for this test (to avoid slow real transcription)
        original_transcribe = services["transcription"].transcribe_audio

        async def mock_transcribe(audio_path, language):
            return "This is a mocked transcription for integration testing", language

        services["transcription"].transcribe_audio = mock_transcribe

        try:
            # Execute voice handling
            await handler.handle_voice(update, context)

            # Verify message was marked as processed
            assert services["state"].is_message_processed("12345")

            # Verify note was added to project
            project_dir = services["project"].get_project_dir(project_id)
            notes_file = project_dir / "notes.md"
            notes_content = notes_file.read_text()

            assert "This is a mocked transcription for integration testing" in notes_content

            # Verify confirmation message
            processing_msg.edit_text.assert_called_once()
            confirmation_text = processing_msg.edit_text.call_args[0][0]
            assert "Added to project" in confirmation_text
            assert "Voice Test Project" in confirmation_text

        finally:
            # Restore original transcription method
            services["transcription"].transcribe_audio = original_transcribe

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_voice_no_active_project_error(self, real_services):
        """Test voice handling error when no project selected"""
        services = real_services.get_all()

        # Ensure no active project
        assert services["state"].get_active_project() is None

        handler = VoiceMessageHandler(services)

        update = Mock()
        update.message = Mock()
        update.message.message_id = 54321
        update.message.reply_text = AsyncMock()
        context = Mock()

        # Execute voice handling
        await handler.handle_voice(update, context)

        # Should get error message
        update.message.reply_text.assert_called_once()
        error_text = update.message.reply_text.call_args[0][0]
        assert "No project selected" in error_text

        # Message should not be marked as processed
        assert not services["state"].is_message_processed("54321")


class TestCommandIntegrationWorkflows:
    """Test complete workflows across multiple commands"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_project_workflow(self, real_services):
        """Test complete workflow: create project -> select -> add note -> check status"""
        services = real_services.get_all()

        # Step 1: Create new project
        new_cmd = NewProjectCommand(services)
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ["Workflow", "Test"]

        await new_cmd.execute(update, context)

        # Find the created project
        projects = services["state"].get_projects()
        project_id = None
        for pid, name in projects.items():
            if name == "Workflow Test":
                project_id = pid
                break

        assert project_id is not None

        # Step 2: Select the project
        projects_cmd = ProjectsCommand(services)
        query = Mock()
        query.data = f"pick_{project_id}"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update2 = Mock()
        update2.callback_query = query
        context2 = Mock()

        await projects_cmd.handle_callback(update2, context2)

        # Verify project is active
        assert services["state"].get_active_project() == project_id

        # Step 3: Add a note directly to project
        services["project"].add_note(
            project_id, "Workflow test note with multiple words for testing"
        )

        # Step 4: Check status
        status_cmd = StatusCommand(services)
        update3 = Mock()
        update3.message = Mock()
        update3.message.reply_text = AsyncMock()
        context3 = Mock()

        await status_cmd.execute(update3, context3)

        # Verify status shows correct information
        status_text = update3.message.reply_text.call_args[0][0]
        assert "Workflow Test" in status_text
        assert "Messages: 1" in status_text
        assert "Total words:" in status_text

        # Step 5: Change language and verify persistence
        lang_cmd = LanguageCommand(services)
        query2 = Mock()
        query2.data = "lang_bg"
        query2.answer = AsyncMock()
        query2.edit_message_text = AsyncMock()

        update4 = Mock()
        update4.callback_query = query2
        context4 = Mock()

        await lang_cmd.handle_callback(update4, context4)

        # Verify language changed
        assert services["state"].get_language() == "bg"

        # Step 6: Check status again to verify language display
        update5 = Mock()
        update5.message = Mock()
        update5.message.reply_text = AsyncMock()
        context5 = Mock()

        await status_cmd.execute(update5, context5)

        status_text2 = update5.message.reply_text.call_args[0][0]
        assert "Bulgarian" in status_text2
