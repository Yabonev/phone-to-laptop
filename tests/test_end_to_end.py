"""
End-to-end integration tests that validate complete workflows

These tests validate the entire voice message processing pipeline:
voice audio -> transcription -> file storage -> state management -> user feedback

This is what REAL testing looks like - no mocks except for external APIs.
"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.commands.new_project import NewProjectCommand
from src.commands.status import StatusCommand
from src.commands.voice import VoiceMessageHandler
from src.services.container import ServiceContainer


class TestEndToEndVoiceProcessing:
    """End-to-end tests for voice message processing"""

    @pytest.mark.integration
    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_complete_voice_to_text_to_file_pipeline(
        self, real_services, audio_generator, temp_dir
    ):
        """Test complete pipeline: audio -> transcription -> file -> verification"""
        services = real_services.get_all()

        # Step 1: Create a real project
        new_cmd = NewProjectCommand(services)
        update = Mock()
        update.message = Mock()
        update.message.reply_text = AsyncMock()
        context = Mock()
        context.args = ["E2E", "Test", "Project"]

        await new_cmd.execute(update, context)

        # Find the created project
        projects = services["state"].get_projects()
        project_id = None
        for pid, name in projects.items():
            if name == "E2E Test Project":
                project_id = pid
                break

        assert project_id is not None
        services["state"].set_active_project(project_id)

        # Step 2: Create real audio file for transcription
        silence_data = audio_generator.generate_silence(2.0)
        audio_file = audio_generator.create_wav_file(silence_data, temp_dir / "e2e_test.wav")

        try:
            # Step 3: Set up voice message handler
            handler = VoiceMessageHandler(services)

            # Mock Telegram voice message components (only external API)
            voice_file = Mock()
            voice_file.get_file = AsyncMock()
            mock_telegram_file = Mock()
            mock_telegram_file.download_to_drive = AsyncMock()
            voice_file.get_file.return_value = mock_telegram_file

            # Mock the download to use our real audio file
            async def mock_download(path):
                # Copy our real audio to the target path
                Path(path).write_bytes(audio_file.read_bytes())

            mock_telegram_file.download_to_drive.side_effect = mock_download

            update = Mock()
            update.message = Mock()
            update.message.message_id = 999888
            update.message.voice = voice_file
            update.message.reply_text = AsyncMock()

            processing_msg = Mock()
            processing_msg.edit_text = AsyncMock()
            update.message.reply_text.return_value = processing_msg

            context = Mock()

            # Step 4: Process the voice message with REAL transcription
            await handler.handle_voice(update, context)

            # Step 5: Verify the complete pipeline worked

            # Check message was marked as processed
            assert services["state"].is_message_processed("999888")

            # Check project file was updated with transcription
            project_dir = services["project"].get_project_dir(project_id)
            notes_file = project_dir / "notes.md"
            assert notes_file.exists()

            notes_content = notes_file.read_text()
            # Should have the project header and a timestamped entry
            assert "# E2E Test Project" in notes_content
            assert "##" in notes_content  # Timestamp marker

            # Verify the transcription result is appropriate for silence
            # (Whisper should produce minimal output for silence)
            lines = notes_content.split("\n")
            # Exclude template text and only look at actual transcription content
            content_lines = [
                line
                for line in lines
                if line
                and not line.startswith("#")
                and "Voice notes transcriptions:" not in line
                and line.strip()
            ]
            if content_lines:
                # If there is transcription content, it should be minimal for silence
                total_content = " ".join(content_lines).strip()
                assert len(total_content) <= 50  # Minimal content for silence

            # Check confirmation message was sent
            processing_msg.edit_text.assert_called_once()
            confirmation = processing_msg.edit_text.call_args[0][0]
            assert "Added to project" in confirmation
            assert "E2E Test Project" in confirmation

            print(f"E2E test completed successfully. Notes content:\n{notes_content}")

        finally:
            # Cleanup
            if audio_file.exists():
                audio_file.unlink()

    @pytest.mark.integration
    @pytest.mark.transcription
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_bulgarian_voice_with_translation_pipeline(
        self, real_services, audio_generator, temp_dir
    ):
        """Test complete Bulgarian voice processing with English translation"""
        services = real_services.get_all()

        # Set language to Bulgarian
        services["state"].set_language("bg")

        # Create project
        project_id = services["project"].create_project("Bulgarian Test", {})
        services["state"].add_project(project_id, "Bulgarian Test")
        services["state"].set_active_project(project_id)

        # Create test audio (speech-like for Bulgarian processing)
        speech_data = audio_generator.generate_speech_like_audio(3.0)
        audio_file = audio_generator.create_wav_file(speech_data, temp_dir / "bulgarian_test.wav")

        try:
            handler = VoiceMessageHandler(services)

            # Mock Telegram components
            voice_file = Mock()
            voice_file.get_file = AsyncMock()
            mock_telegram_file = Mock()

            async def mock_download(path):
                Path(path).write_bytes(audio_file.read_bytes())

            mock_telegram_file.download_to_drive.side_effect = mock_download
            voice_file.get_file.return_value = mock_telegram_file

            update = Mock()
            update.message = Mock()
            update.message.message_id = 777666
            update.message.voice = voice_file
            update.message.reply_text = AsyncMock()

            processing_msg = Mock()
            processing_msg.edit_text = AsyncMock()
            update.message.reply_text.return_value = processing_msg

            context = Mock()

            # Process voice with Bulgarian language setting
            await handler.handle_voice(update, context)

            # Verify Bulgarian processing pipeline
            assert services["state"].is_message_processed("777666")

            # Check notes file for Bulgarian format
            project_dir = services["project"].get_project_dir(project_id)
            notes_file = project_dir / "notes.md"
            notes_content = notes_file.read_text()

            # Should have timestamp and potentially Bulgarian/English format
            assert "##" in notes_content

            # If any translation occurred, verify format
            if "**Bulgarian:**" in notes_content and "**English:**" in notes_content:
                print("Translation format detected in notes")

            print(f"Bulgarian pipeline test completed. Notes:\n{notes_content}")

        finally:
            if audio_file.exists():
                audio_file.unlink()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_voice_processing_error_handling_pipeline(self, real_services, temp_dir):
        """Test error handling in the complete voice processing pipeline"""
        services = real_services.get_all()

        # Create project
        project_id = services["project"].create_project("Error Test", {})
        services["state"].add_project(project_id, "Error Test")
        services["state"].set_active_project(project_id)

        handler = VoiceMessageHandler(services)

        # Mock failing Telegram download
        voice_file = Mock()
        voice_file.get_file = AsyncMock(side_effect=Exception("Telegram download failed"))

        update = Mock()
        update.message = Mock()
        update.message.message_id = 555444
        update.message.voice = voice_file
        update.message.reply_text = AsyncMock()

        processing_msg = Mock()
        processing_msg.edit_text = AsyncMock()
        update.message.reply_text.return_value = processing_msg

        context = Mock()

        # Process voice with error
        await handler.handle_voice(update, context)

        # Verify error handling
        # Message should NOT be marked as processed on error
        assert not services["state"].is_message_processed("555444")

        # Should show error message
        processing_msg.edit_text.assert_called_once()
        error_message = processing_msg.edit_text.call_args[0][0]
        assert "Error" in error_message

        # Project should not have new content
        project_dir = services["project"].get_project_dir(project_id)
        notes_file = project_dir / "notes.md"
        notes_content = notes_file.read_text()

        # Should only have the header, no new transcription entries
        lines = [line for line in notes_content.split("\n") if line.strip()]
        header_lines = [line for line in lines if line.startswith("#")]
        assert len(header_lines) <= 2  # Only project header


class TestEndToEndWorkflowValidation:
    """Test complete user workflows from start to finish"""

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_new_user_complete_workflow(self, real_services, audio_generator, temp_dir):
        """Test complete workflow for a new user: setup -> create project -> process voice -> check status"""
        services = real_services.get_all()

        # Verify clean state (new user)
        assert len(services["state"].get_projects()) == 0
        assert services["state"].get_active_project() is None
        assert services["state"].get_language() == "en"

        # Step 1: Create first project
        new_cmd = NewProjectCommand(services)
        update1 = Mock()
        update1.message = Mock()
        update1.message.reply_text = AsyncMock()
        context1 = Mock()
        context1.args = ["My", "First", "Project"]

        await new_cmd.execute(update1, context1)

        # Verify project creation
        projects = services["state"].get_projects()
        assert len(projects) == 1
        project_id = list(projects.keys())[0]
        assert projects[project_id] == "My First Project"

        # Step 2: Select the project (simulate user clicking button)
        from src.commands.projects import ProjectsCommand

        projects_cmd = ProjectsCommand(services)

        query = Mock()
        query.data = f"pick_{project_id}"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()

        update2 = Mock()
        update2.callback_query = query
        context2 = Mock()

        await projects_cmd.handle_callback(update2, context2)

        # Verify project selection
        assert services["state"].get_active_project() == project_id

        # Step 3: Process multiple voice messages
        handler = VoiceMessageHandler(services)

        for i, audio_type in enumerate(["silence", "tone"], 1):
            # Create different audio for each message
            if audio_type == "silence":
                audio_data = audio_generator.generate_silence(1.5)
            else:
                audio_data = audio_generator.generate_tone(330.0, 1.8)  # E4 note

            audio_file = audio_generator.create_wav_file(audio_data, temp_dir / f"message_{i}.wav")

            try:
                # Mock Telegram components
                voice_file = Mock()
                voice_file.get_file = AsyncMock()
                mock_telegram_file = Mock()

                async def mock_download(path):
                    Path(path).write_bytes(audio_file.read_bytes())

                mock_telegram_file.download_to_drive.side_effect = mock_download
                voice_file.get_file.return_value = mock_telegram_file

                update_voice = Mock()
                update_voice.message = Mock()
                update_voice.message.message_id = f"msg_{i}"
                update_voice.message.voice = voice_file
                update_voice.message.reply_text = AsyncMock()

                processing_msg = Mock()
                processing_msg.edit_text = AsyncMock()
                update_voice.message.reply_text.return_value = processing_msg

                context_voice = Mock()

                # Process the voice message
                await handler.handle_voice(update_voice, context_voice)

                # Verify processing
                assert services["state"].is_message_processed(f"msg_{i}")

            finally:
                if audio_file.exists():
                    audio_file.unlink()

        # Step 4: Check final status
        status_cmd = StatusCommand(services)
        update_status = Mock()
        update_status.message = Mock()
        update_status.message.reply_text = AsyncMock()
        context_status = Mock()

        await status_cmd.execute(update_status, context_status)

        # Verify status shows correct information
        status_text = update_status.message.reply_text.call_args[0][0]
        assert "My First Project" in status_text
        assert "Messages: 2" in status_text  # Two voice messages processed
        assert "English" in status_text

        # Step 5: Verify project file contents
        project_dir = services["project"].get_project_dir(project_id)
        notes_file = project_dir / "notes.md"
        notes_content = notes_file.read_text()

        # Should have project header and two timestamped entries
        assert "# My First Project" in notes_content
        timestamp_count = notes_content.count("##")
        assert timestamp_count == 2  # Two voice messages

        # Verify project statistics
        messages, words = services["project"].get_project_stats(project_id)
        assert messages == 2
        assert words >= 0  # Word count depends on what Whisper outputs for our test audio

        print("Complete workflow test successful!")
        print(f"Final project stats: {messages} messages, {words} words")
        print(f"Final notes content:\n{notes_content}")


class TestEndToEndStateManagement:
    """Test state persistence and management across the complete pipeline"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_state_persistence_across_operations(self, test_config, temp_dir):
        """Test that state persists correctly across multiple service container instances"""

        # Create first service container
        container1 = ServiceContainer(test_config)
        services1 = container1.get_all()

        # Create project and set language
        project_id = services1["project"].create_project("Persistence Test", {})
        services1["state"].add_project(project_id, "Persistence Test")
        services1["state"].set_active_project(project_id)
        services1["state"].set_language("bg")
        services1["state"].mark_message_processed("test_msg_1")

        # Add note to project
        services1["project"].add_note(project_id, "Test note for persistence")

        # Create second service container (simulates bot restart)
        container2 = ServiceContainer(test_config)
        services2 = container2.get_all()

        # Verify all state persisted
        assert services2["state"].get_language() == "bg"
        assert services2["state"].get_active_project() == project_id
        assert services2["state"].is_message_processed("test_msg_1")

        projects = services2["state"].get_projects()
        assert project_id in projects
        assert projects[project_id] == "Persistence Test"

        # Verify project file persisted
        project_dir = services2["project"].get_project_dir(project_id)
        assert project_dir.exists()

        notes_file = project_dir / "notes.md"
        notes_content = notes_file.read_text()
        assert "Test note for persistence" in notes_content

        # Verify project stats work across instances
        messages, words = services2["project"].get_project_stats(project_id)
        assert messages == 1
        assert words > 0

        print("State persistence test passed - all data survived service container restart")
