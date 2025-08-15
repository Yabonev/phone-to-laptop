"""
New project command - Create a new project
"""
from telegram import Update
from telegram.ext import ContextTypes
from src.core.command import Command


class NewProjectCommand(Command):
    """Handle /new command to create projects"""
    
    @property
    def name(self) -> str:
        return "new"
    
    @property
    def description(self) -> str:
        return "Create new project"
    
    @property
    def menu_icon(self) -> str:
        return "➕"
    
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Create a new project"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /new <project_name>")
            return
        
        project_name = " ".join(context.args)
        
        # Create project
        existing_projects = self.state.get_projects()
        project_id = self.project_service.create_project(project_name, existing_projects)
        
        # Save to state
        self.state.add_project(project_id, project_name)
        
        await update.message.reply_text(f'✅ Created project "{project_name}" (ID: {project_id})')
        self.logger.info(f"Created project {project_id}: {project_name}")