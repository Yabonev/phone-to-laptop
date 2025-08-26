"""
Start command - Shows welcome message
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.commands.base import Command


class StartCommand(Command):
    """Handle /start command"""

    @property
    def name(self) -> str:
        return "start"

    @property
    def description(self) -> str:
        return "Start the bot"

    @property
    def show_in_menu(self) -> bool:
        return False  # Start is implicit, no need in menu

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show welcome message"""
        lang = self.state.get_language()
        lang_name = {"en": "English", "bg": "Bulgarian", "auto": "Auto-detect"}.get(lang, lang)

        active_project = self.state.get_active_project()
        project_name = None
        if active_project:
            projects = self.state.get_projects()
            project_name = projects.get(active_project)

        message = (
            "🎤 Voice Notes Bot\n\n"
            "💡 Type / to see all commands\n\n"
            f"🌐 Language: {lang_name}\n"
            "Quick set: /language\n\n"
        )

        if project_name:
            message += f'📂 Active: "{project_name}"\n'
        else:
            message += "⚠️ No project selected. Use /projects\n"

        message += "\n💡 Send voice messages after selecting a project!"

        await update.message.reply_text(message)
        self.logger.info(f"User {update.effective_user.id} started bot")
