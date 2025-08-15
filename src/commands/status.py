"""
Status command - Show current project status
"""
from telegram import Update
from telegram.ext import ContextTypes
from src.core.command import Command


class StatusCommand(Command):
    """Handle /status command"""
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def description(self) -> str:
        return "Show current status"
    
    @property
    def menu_icon(self) -> str:
        return "📊"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show project status with statistics"""
        active_project = self.state.get_active_project()
        
        if not active_project:
            await update.message.reply_text("❌ No active project. Use /projects to select one.")
            return
        
        projects = self.state.get_projects()
        project_name = projects.get(active_project)
        
        if not project_name:
            await update.message.reply_text("❌ Active project not found.")
            return
        
        # Get statistics
        message_count, total_words = self.project_service.get_project_stats(active_project)
        
        # Get language
        lang = self.state.get_language()
        lang_name = {"en": "English", "bg": "Bulgarian", "auto": "Auto-detect"}.get(lang, lang)
        
        await update.message.reply_text(
            f'📂 Project: "{project_name}" (ID: {active_project})\n'
            f'📝 Messages: {message_count}\n'
            f'📊 Total words: {total_words}\n'
            f'🌐 Language: {lang_name}'
        )