"""
Base command interface following SOLID principles
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes


class Command(ABC):
    """Base command interface - all commands must implement this"""
    
    def __init__(self, services: Dict[str, Any]):
        """Initialize with injected services"""
        self.services = services
        self.state = services.get('state')
        self.project_service = services.get('project')
        self.transcription = services.get('transcription')
        self.logger = services.get('logger')
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (e.g., 'start', 'projects')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Command description for menu"""
        pass
    
    @property
    def menu_icon(self) -> str:
        """Optional icon for command menu"""
        return ""
    
    @property
    def show_in_menu(self) -> bool:
        """Whether to show this command in the bot menu"""
        return True
    
    @abstractmethod
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Execute the command"""
        pass
    
    async def can_execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if command can be executed (for conditional commands)"""
        return True


class CallbackCommand(Command):
    """Base class for commands that handle button callbacks"""
    
    @abstractmethod
    def get_callback_patterns(self) -> List[str]:
        """Return list of callback data patterns this command handles"""
        pass
    
    @abstractmethod
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callback"""
        pass


class VoiceCommand(Command):
    """Base class for commands that handle voice messages"""
    
    @abstractmethod
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice message"""
        pass