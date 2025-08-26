"""
Projects command - List and manage projects
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot.commands.base import CallbackCommand


class ProjectsCommand(CallbackCommand):
    """Handle /projects command and project selection/deletion"""

    @property
    def name(self) -> str:
        return "projects"

    @property
    def description(self) -> str:
        return "List and select projects"

    @property
    def menu_icon(self) -> str:
        return "📁"

    def get_callback_patterns(self) -> list[str]:
        """Patterns this command handles"""
        return ["pick_", "del_", "confirm_del_", "cancel_del"]

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show projects list with buttons"""
        projects = self.state.get_projects()

        if not projects:
            await update.message.reply_text("📂 No projects yet. Create one with /new <name>")
            return

        # Create buttons (newest first)
        keyboard = []
        sorted_projects = sorted(projects.items(), key=lambda x: x[0], reverse=True)

        for pid, name in sorted_projects:
            padded_name = f"📂 {pid}. {name}                    "
            keyboard.append(
                [
                    InlineKeyboardButton(padded_name, callback_data=f"pick_{pid}"),
                    InlineKeyboardButton("📦", callback_data=f"del_{pid}"),  # Archive icon
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📁 Select or archive a project:", reply_markup=reply_markup
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button presses"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith("pick_"):
            await self._handle_project_selection(query, data.replace("pick_", ""))
        elif data.startswith("del_"):
            await self._handle_delete_request(query, data.replace("del_", ""))
        elif data.startswith("confirm_del_"):
            await self._handle_delete_confirmation(query, data.replace("confirm_del_", ""))
        elif data == "cancel_del":
            await query.edit_message_text(
                "✅ Deletion cancelled. Use /projects to see your projects."
            )

    async def _handle_project_selection(self, query, project_id: str):
        """Handle project selection"""
        projects = self.state.get_projects()

        if project_id not in projects:
            await query.edit_message_text(f"❌ Project {project_id} not found.")
            return

        self.state.set_active_project(project_id)
        project_name = projects[project_id]

        await query.edit_message_text(
            f'✅ Selected project "{project_name}"\n🎤 Send voice messages...'
        )
        self.logger.info(f"User selected project {project_id}")

    async def _handle_delete_request(self, query, project_id: str):
        """Show archive confirmation"""
        projects = self.state.get_projects()

        if project_id not in projects:
            await query.edit_message_text(f"❌ Project {project_id} not found.")
            return

        project_name = projects[project_id]

        keyboard = [
            [
                InlineKeyboardButton("📦 Yes, archive", callback_data=f"confirm_del_{project_id}"),
                InlineKeyboardButton("✅ Keep active", callback_data="cancel_del"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f'📦 Archive project "{project_name}"?\n\n'
            "This will move the project to the archive folder.\n"
            "You can find it later in the /archive directory.",
            reply_markup=reply_markup,
        )

    async def _handle_delete_confirmation(self, query, project_id: str):
        """Archive the project"""
        projects = self.state.get_projects()

        if project_id not in projects:
            await query.edit_message_text(f"❌ Project {project_id} not found.")
            return

        project_name = projects[project_id]

        # Archive project (move to archive folder)
        self.project_service.archive_project(project_id)

        # Remove from active state
        self.state.remove_project(project_id)

        await query.edit_message_text(
            f'📦 Archived project "{project_name}"\n\n'
            f"Project moved to /archive folder with timestamp."
        )
        self.logger.info(f"Archived project {project_id}")
