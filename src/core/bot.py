"""
Main bot class - thin layer that coordinates everything
"""
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application
from .registry import CommandRegistry
from ..services.container import ServiceContainer


class VoiceNotesBot:
    """Main bot - follows Open/Closed and Dependency Inversion principles"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.container = ServiceContainer(config)
        
        # Initialize command registry
        self.registry = CommandRegistry()
        
        # Create required directories
        self._create_directories()
    
    def _create_directories(self):
        """Create required directories"""
        dirs = [
            Path(self.config.get('projects_dir', './projects')),
            Path(self.config.get('audio_dir', './audio')),
            Path(self.config.get('logs_dir', './logs'))
        ]
        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True)
    
    def register_command(self, command_class):
        """Register a command - Open for extension"""
        services = self.container.get_all()
        command = command_class(services)
        self.registry.register(command)
        self.logger.info(f"Registered command: {command.name}")
    
    def register_commands(self, *command_classes):
        """Register multiple commands"""
        for command_class in command_classes:
            self.register_command(command_class)
    
    async def process_queued_messages(self, application: Application):
        """Process messages that were sent while bot was offline"""
        self.logger.info("🔍 Checking for queued messages...")
        
        state = self.container.get('state')
        
        try:
            updates = await application.bot.get_updates(
                offset=state.state.last_update_id + 1 if state.state.last_update_id else 0
            )
            
            if updates:
                self.logger.info(f"📬 Found {len(updates)} messages in queue")
                
                # Notify user about processing queued messages
                if updates and updates[0].message and updates[0].message.from_user:
                    try:
                        await application.bot.send_message(
                            chat_id=updates[0].message.from_user.id,
                            text=f"💻 Laptop is back online!\n📬 Processing {len(updates)} queued messages..."
                        )
                    except Exception as e:
                        self.logger.error(f"Could not send queue notification: {e}")
                
                for update in updates:
                    state.update_last_update_id(update.update_id)
                    
                    # Process based on update type
                    if update.message and update.message.voice:
                        if self.registry.voice_handler:
                            await self.registry.voice_handler.handle_voice(update, None)
                    elif update.message and update.message.text:
                        text = update.message.text
                        if text.startswith('/'):
                            # Extract command name
                            command_name = text.split()[0][1:]  # Remove /
                            command = self.registry.get_command(command_name)
                            if command:
                                # Create minimal context for args
                                parts = text.split(maxsplit=1)
                                context = type('obj', (object,), {
                                    'args': parts[1].split() if len(parts) > 1 else []
                                })()
                                await command.execute(update, context)
                
                self.logger.info(f"✅ Processed {len(updates)} queued messages")
            else:
                self.logger.info("📭 No queued messages found")
                
        except Exception as e:
            self.logger.error(f"Error processing queued messages: {e}")
    
    async def setup_bot_menu(self, application: Application):
        """Set up bot commands menu"""
        bot_commands = self.registry.get_bot_commands()
        await application.bot.set_my_commands(bot_commands)
        self.logger.info("Bot commands menu set")
    
    def run(self):
        """Run the bot"""
        token = self.config.get('telegram_token')
        if not token:
            self.logger.error("TELEGRAM_TOKEN not configured")
            return
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Store bot instance for callbacks
        application.bot_data['bot_instance'] = self
        
        # Register all handlers from registry
        handlers = self.registry.get_telegram_handlers(application)
        for handler in handlers:
            application.add_handler(handler)
        
        # Setup startup tasks
        async def startup_callback(app: Application):
            bot_instance = app.bot_data['bot_instance']
            await bot_instance.setup_bot_menu(app)
            # Run cleanup before processing messages
            cleanup_service = bot_instance.container.get('cleanup')
            if cleanup_service:
                cleanup_service.run_cleanup()
            await bot_instance.process_queued_messages(app)
        
        application.post_init = startup_callback
        
        # Start bot
        self.logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)