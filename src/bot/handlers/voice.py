"""
Voice command - Handle voice messages
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.commands.base import VoiceCommand


class VoiceMessageHandler(VoiceCommand):
    """Handle voice messages"""

    @property
    def name(self) -> str:
        return "voice_handler"

    @property
    def description(self) -> str:
        return "Process voice messages"

    @property
    def show_in_menu(self) -> bool:
        return False

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Not used for voice handlers"""
        pass

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process voice message"""
        message_id = str(update.message.message_id)

        # Check if already processed
        if self.state.is_message_processed(message_id):
            self.logger.info(f"Skipping already processed message {message_id}")
            return

        # Check active project
        active_project = self.state.get_active_project()
        if not active_project:
            await update.message.reply_text("❌ No project selected. Use /projects first.")
            return

        projects = self.state.get_projects()
        project_name = projects.get(active_project)

        if not project_name:
            await update.message.reply_text("❌ Project not found.")
            return

        # Send processing indicator
        processing_msg = await update.message.reply_text("📝 Processing...")

        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            audio_path = self.transcription.create_temp_audio_file()
            await voice_file.download_to_drive(audio_path)

            # Get language setting (default to English)
            language = self.state.get_language()
            if language not in ["en", "bg"]:
                language = "en"  # Default to English if invalid

            # Transcribe
            text, lang_used = await self.transcription.transcribe_audio(audio_path, language)

            # Translate only if Bulgarian is explicitly selected
            translation = None
            if language == "bg":
                self.logger.info("Getting English translation...")
                translation = await self.transcription.translate_to_english(audio_path, "bg")

            # Clean up audio
            self.transcription.cleanup_audio_file(audio_path)

            # Save to project
            self.project_service.add_note(active_project, text, translation)

            # Mark as processed
            self.state.mark_message_processed(message_id)

            # Send confirmation with preview
            words = text.split()
            word_count = len(words)

            # Get first 10 words for preview (more context is better)
            preview = " ".join(words[:10])
            if len(words) > 10:
                preview += "..."

            # Format with clear visual hierarchy
            confirmation = (
                f'✅ Added to project "{project_name}"\n'
                f"📝 {word_count} words transcribed\n\n"
                f'💬 "{preview}"'
            )

            await processing_msg.edit_text(confirmation)

            self.logger.info(f"Transcribed {word_count} words to project {active_project}")

        except Exception as e:
            self.logger.error(f"Error processing voice message: {e}")
            await processing_msg.edit_text(f"❌ Error: {str(e)}")
