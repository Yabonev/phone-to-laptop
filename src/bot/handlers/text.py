"""
Text command - Handle text messages
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.commands.base import TextCommand


class TextMessageHandler(TextCommand):
    """Handle text messages"""

    @property
    def name(self) -> str:
        return "text_handler"

    @property
    def description(self) -> str:
        return "Process text messages"

    @property
    def show_in_menu(self) -> bool:
        return False

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Not used for text handlers"""
        pass

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process text message"""
        message_id = str(update.message.message_id)

        # Check if already processed
        if self.state.is_message_processed(message_id):
            self.logger.info(f"Skipping already processed text message {message_id}")
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

        # Get message text
        text_content = update.message.text
        if not text_content:
            self.logger.warning("Received empty text message")
            return

        try:
            # Save to project as text note
            self.project_service.add_text_note(active_project, text_content)

            # Mark as processed
            self.state.mark_message_processed(message_id)

            # Send confirmation with preview
            words = text_content.split()
            word_count = len(words)

            # Get first 10 words for preview
            preview = " ".join(words[:10])
            if len(words) > 10:
                preview += "..."

            # Format confirmation
            confirmation = (
                f'📝 Added to project "{project_name}"\n'
                f"✏️ {word_count} words logged\n\n"
                f'💭 "{preview}"'
            )

            await update.message.reply_text(confirmation)

            self.logger.info(f"Logged {word_count} words of text to project {active_project}")

        except Exception as e:
            self.logger.error(f"Error processing text message: {e}")
            await update.message.reply_text(f"❌ Error logging message: {str(e)}")
