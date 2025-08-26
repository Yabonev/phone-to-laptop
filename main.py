#!/usr/bin/env python3
"""
Voice Notes Bot - Clean Architecture Implementation
Following SOLID principles for maintainable, extensible code
"""

import logging
import os

from dotenv import load_dotenv
from rich.logging import RichHandler

from src.bot.commands.language import LanguageCommand
from src.bot.commands.new_project import NewProjectCommand
from src.bot.commands.projects import ProjectsCommand

# Import commands - each is a separate, pluggable module
from src.bot.commands.start import StartCommand
from src.bot.commands.status import StatusCommand
from src.bot.handlers.text import TextMessageHandler
from src.bot.handlers.voice import VoiceMessageHandler

# Import core
from src.bot.app import VoiceNotesBot

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True), logging.FileHandler("runtime/logs/bot.log", mode="a")],
)


def load_config():
    """Load configuration from environment"""
    return {
        "telegram_token": os.getenv("TELEGRAM_TOKEN"),
        "whisper_model": os.getenv("WHISPER_MODEL", "large"),
        "projects_dir": os.getenv("PROJECTS_DIR", "./runtime/data/projects"),
        "audio_dir": os.getenv("AUDIO_DIR", "./runtime/audio"),
        "logs_dir": os.getenv("LOGS_DIR", "./runtime/logs"),
        "state_file": "./runtime/data/state.json",
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
        TextMessageHandler,
    )

    # Example: Adding a custom command is as simple as:
    # from src.commands.custom import CustomCommand
    # bot.register_command(CustomCommand)

    # Run the bot
    bot.run()


if __name__ == "__main__":
    main()
