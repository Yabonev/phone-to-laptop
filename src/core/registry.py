"""
Command registry for dynamic command management
"""
from typing import Dict, List, Type, Any
from telegram import BotCommand
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
from .command import Command, CallbackCommand, VoiceCommand


class CommandRegistry:
    """Registry for all bot commands - Open/Closed Principle"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.callback_handlers: Dict[str, CallbackCommand] = {}
        self.voice_handler: VoiceCommand = None
    
    def register(self, command: Command) -> None:
        """Register a new command"""
        self.commands[command.name] = command
        
        # Register callback patterns if it's a callback command
        if isinstance(command, CallbackCommand):
            for pattern in command.get_callback_patterns():
                self.callback_handlers[pattern] = command
        
        # Register as voice handler if it's a voice command
        if isinstance(command, VoiceCommand):
            self.voice_handler = command
    
    def unregister(self, command_name: str) -> None:
        """Remove a command from registry"""
        if command_name in self.commands:
            command = self.commands[command_name]
            
            # Remove callback patterns
            if isinstance(command, CallbackCommand):
                for pattern in command.get_callback_patterns():
                    self.callback_handlers.pop(pattern, None)
            
            # Remove voice handler
            if isinstance(command, VoiceCommand) and self.voice_handler == command:
                self.voice_handler = None
            
            del self.commands[command_name]
    
    def get_command(self, name: str) -> Command:
        """Get command by name"""
        return self.commands.get(name)
    
    def get_callback_handler(self, callback_data: str) -> CallbackCommand:
        """Get handler for callback data"""
        # Find matching pattern
        for pattern, handler in self.callback_handlers.items():
            if callback_data.startswith(pattern):
                return handler
        return None
    
    def get_telegram_handlers(self, application):
        """Get all Telegram handlers for registered commands"""
        handlers = []
        
        # Add command handlers
        for name, command in self.commands.items():
            # Skip voice handlers as they use MessageHandler
            if not isinstance(command, VoiceCommand):
                handlers.append(
                    CommandHandler(name, lambda u, c, cmd=command: cmd.execute(u, c))
                )
        
        # Add callback query handler
        if self.callback_handlers:
            async def callback_handler(update, context):
                query = update.callback_query
                # Find the right handler
                for pattern, command in self.callback_handlers.items():
                    if query.data.startswith(pattern):
                        await command.handle_callback(update, context)
                        return
            
            handlers.append(CallbackQueryHandler(callback_handler))
        
        # Add voice handler
        if self.voice_handler:
            handlers.append(
                MessageHandler(filters.VOICE, self.voice_handler.handle_voice)
            )
        
        return handlers
    
    def get_bot_commands(self) -> List[BotCommand]:
        """Get command list for Telegram menu"""
        bot_commands = []
        for name, command in self.commands.items():
            if command.show_in_menu:
                description = f"{command.menu_icon} {command.description}" if command.menu_icon else command.description
                bot_commands.append(BotCommand(name, description))
        return bot_commands