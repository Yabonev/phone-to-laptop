#!/usr/bin/env python3
"""
Voice Notes Bot - Clean Architecture Implementation
Following SOLID principles for maintainable, extensible code
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from rich.logging import RichHandler

# Import core
from src.core.bot import VoiceNotesBot

# Import commands - each is a separate, pluggable module
from src.commands.start import StartCommand
from src.commands.projects import ProjectsCommand
from src.commands.new_project import NewProjectCommand
from src.commands.status import StatusCommand
from src.commands.language import LanguageCommand
from src.commands.voice import VoiceMessageHandler

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler("logs/bot.log", mode='a')
    ]
)


def load_config():
    """Load configuration from environment"""
    return {
        'telegram_token': os.getenv('TELEGRAM_TOKEN'),
        'whisper_model': os.getenv('WHISPER_MODEL', 'large'),
        'projects_dir': os.getenv('PROJECTS_DIR', './projects'),
        'audio_dir': os.getenv('AUDIO_DIR', './audio'),
        'logs_dir': os.getenv('LOGS_DIR', './logs'),
        'state_file': 'state.json'
    }


def main():
    """
    Main entry point - demonstrates clean architecture:
    1. Load configuration
    2. Create bot
    3. Register commands (pluggable - add/remove without touching bot code)
    4. Run
    """
    # Load configuration
    config = load_config()
    
    # Create bot instance
    bot = VoiceNotesBot(config)
    
    # Register commands - OPEN/CLOSED PRINCIPLE
    # You can add/remove commands here without modifying any other code
    bot.register_commands(
        StartCommand,
        ProjectsCommand,
        NewProjectCommand,
        StatusCommand,
        LanguageCommand,
        VoiceMessageHandler,
    )
    
    # Example: Adding a custom command is as simple as:
    # from src.commands.custom import CustomCommand
    # bot.register_command(CustomCommand)
    
    # Run the bot
    bot.run()


if __name__ == "__main__":
    main()
