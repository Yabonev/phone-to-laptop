#!/usr/bin/env python3
"""
Telegram Voice Notes Bot - Captures voice messages and transcribes them to project folders
"""

import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

import whisper
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.logging import RichHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load environment variables
load_dotenv()

# Setup logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True), logging.FileHandler("logs/bot.log", mode="a")],
)
logger = logging.getLogger(__name__)


# Configuration
class Config(BaseModel):
    telegram_token: str = Field(default_factory=lambda: os.getenv("TELEGRAM_TOKEN", ""))
    whisper_model: str = Field(default_factory=lambda: os.getenv("WHISPER_MODEL", "base"))
    projects_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("PROJECTS_DIR", "./projects"))
    )
    audio_dir: Path = Field(default_factory=lambda: Path(os.getenv("AUDIO_DIR", "./audio")))
    logs_dir: Path = Field(default_factory=lambda: Path(os.getenv("LOGS_DIR", "./logs")))
    timezone: str = Field(default_factory=lambda: os.getenv("TIMEZONE", "UTC"))
    check_interval: int = Field(default_factory=lambda: int(os.getenv("CHECK_INTERVAL", "60")))
    offline_response: str = Field(
        default_factory=lambda: os.getenv(
            "OFFLINE_RESPONSE", "💻 Laptop is offline. Message queued for processing."
        )
    )


# State management
class BotState(BaseModel):
    last_update_id: int | None = None
    active_project: str | None = None  # Single active project
    processed_messages: list[str] = Field(default_factory=list)
    projects: dict[str, str] = Field(default_factory=dict)  # project_id -> project_name
    language: str = "en"  # Single language setting


class VoiceNotesBot:
    def __init__(self, config: Config):
        self.config = config
        self.state_file = Path("state.json")
        self.state = self.load_state()
        self.whisper_model = None

        # Create directories
        self.config.projects_dir.mkdir(exist_ok=True)
        self.config.audio_dir.mkdir(exist_ok=True)
        self.config.logs_dir.mkdir(exist_ok=True)

        logger.info(f"Bot initialized with projects dir: {self.config.projects_dir}")

    def load_state(self) -> BotState:
        """Load bot state from file"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                return BotState(**data)
        return BotState()

    def save_state(self):
        """Save bot state to file"""
        with open(self.state_file, "w") as f:
            json.dump(self.state.model_dump(), f, indent=2)

    def load_whisper(self):
        """Load Whisper model (lazy loading)"""
        if self.whisper_model is None:
            logger.info(f"Loading Whisper model: {self.config.whisper_model}")
            self.whisper_model = whisper.load_model(self.config.whisper_model)
            logger.info("Whisper model loaded successfully")

    def get_help_message(self, user_id: str) -> str:
        """Get help message with current user settings"""
        lang_name = {"en": "English", "bg": "Bulgarian", "auto": "Auto-detect"}.get(
            self.state.language, self.state.language
        )

        # Check if user has active project
        active_project = None
        if user_id in self.state.active_sessions:
            project_id = self.state.active_sessions[user_id]
            active_project = self.state.projects.get(project_id)

        message = (
            "🎤 Voice Notes Bot\n\n"
            "💡 Type / to see all commands\n"
            "/projects to select a project\n\n"
            "🌐 Language: " + lang_name + "\n"
            "Quick set: /language en or /language bg\n\n"
        )

        if active_project:
            message += f'📂 Active: "{active_project}"\n'
        else:
            message += "⚠️ No project selected\n"

        message += "\n💡 Send voice messages after selecting a project!"
        return message

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = str(update.effective_user.id)

        # Set default language to English if not set
        if user_id not in self.state.user_languages:
            self.state.user_languages[user_id] = "en"
            self.save_state()

        await update.message.reply_text(self.get_help_message(user_id))
        logger.info(f"User {user_id} started bot")

    async def projects_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /projects command"""
        if not self.state.projects:
            await update.message.reply_text("📂 No projects yet. Create one with /new <name>")
            return

        # Create buttons for project selection (newest first)
        keyboard = []
        # Sort projects by ID in reverse order (newest first)
        sorted_projects = sorted(self.state.projects.items(), key=lambda x: x[0], reverse=True)

        for pid, name in sorted_projects:
            # Add select and delete buttons with padding to make project button larger
            # Pad the project name to make it take more visual space
            padded_name = f"📂 {pid}. {name}                    "
            keyboard.append(
                [
                    InlineKeyboardButton(padded_name, callback_data=f"pick_{pid}"),
                    InlineKeyboardButton("🗑️", callback_data=f"del_{pid}"),
                ]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📁 Select or delete a project:", reply_markup=reply_markup)

    async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /new <name> command"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /new <project_name>")
            return

        project_name = " ".join(context.args)
        # Sanitize project name for filesystem
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (" ", "-", "_")).rstrip()

        # Generate project ID (3-digit) - find the highest ID and add 1
        if self.state.projects:
            max_id = max(int(pid) for pid in self.state.projects.keys())
            project_id = str(max_id + 1).zfill(3)
        else:
            project_id = "001"

        # Create project directory
        project_dir = (
            self.config.projects_dir / f"project-{project_id}-{safe_name.replace(' ', '-').lower()}"
        )
        project_dir.mkdir(exist_ok=True)

        # Create notes file
        notes_file = project_dir / "notes.md"
        notes_file.write_text(f"# {project_name}\n\nVoice notes transcriptions:\n\n")

        # Save to state
        self.state.projects[project_id] = project_name
        self.save_state()

        await update.message.reply_text(f'✅ Created project "{project_name}" (ID: {project_id})')
        logger.info(f"Created project {project_id}: {project_name}")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = str(update.effective_user.id)

        if user_id not in self.state.active_sessions:
            await update.message.reply_text("❌ No active project. Use /pick <id> to select one.")
            return

        project_id = self.state.active_sessions[user_id]
        project_name = self.state.projects[project_id]

        # Get project statistics
        project_dir = None
        for dir in self.config.projects_dir.iterdir():
            if dir.name.startswith(f"project-{project_id}-"):
                project_dir = dir
                break

        message_count = 0
        total_words = 0

        if project_dir:
            notes_file = project_dir / "notes.md"
            if notes_file.exists():
                content = notes_file.read_text()
                # Count sections (each voice message creates a ## timestamp section)
                message_count = content.count("\n## ")
                # Count words (excluding markdown headers and empty lines)
                lines = content.split("\n")
                for line in lines:
                    if line and not line.startswith("#"):
                        total_words += len(line.split())

        lang_name = {"en": "English", "bg": "Bulgarian", "auto": "Auto-detect"}.get(
            self.state.language, self.state.language
        )

        await update.message.reply_text(
            f'📂 Project: "{project_name}" (ID: {project_id})\n'
            f"📝 Messages: {message_count}\n"
            f"📊 Total words: {total_words}\n"
            f"🌐 Language: {lang_name}"
        )

    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        user_id = str(update.effective_user.id)
        current_lang = self.state.user_languages.get(user_id, "en")

        # Create language selection buttons
        keyboard = [
            [
                InlineKeyboardButton(
                    "🇬🇧 English" + (" ✓" if current_lang == "en" else ""), callback_data="lang_en"
                )
            ],
            [
                InlineKeyboardButton(
                    "🇧🇬 Bulgarian" + (" ✓" if current_lang == "bg" else ""), callback_data="lang_bg"
                )
            ],
            [
                InlineKeyboardButton(
                    "🤖 Auto-detect" + (" ✓" if current_lang == "auto" else ""),
                    callback_data="lang_auto",
                )
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🌐 Select transcription language:", reply_markup=reply_markup
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        user_id = str(query.from_user.id)

        # Acknowledge the button press
        await query.answer()

        # Handle project selection
        if query.data.startswith("pick_"):
            project_id = query.data.replace("pick_", "")

            if project_id not in self.state.projects:
                await query.edit_message_text(f"❌ Project {project_id} not found.")
                return

            # Set active project
            self.state.active_sessions[user_id] = project_id
            self.save_state()

            project_name = self.state.projects[project_id]
            await query.edit_message_text(
                f'✅ Selected project "{project_name}"\n🎤 Send voice messages...'
            )
            logger.info(f"User {user_id} selected project {project_id} via button")

        # Handle language selection
        elif query.data.startswith("lang_"):
            lang_code = query.data.replace("lang_", "")

            self.state.user_languages[user_id] = lang_code
            self.save_state()

            lang_names = {"en": "English", "bg": "Bulgarian", "auto": "Auto-detect"}

            lang_name = lang_names.get(lang_code, lang_code)
            await query.edit_message_text(f"✅ Language set to: {lang_name}")
            logger.info(f"User {user_id} set language to {lang_code} via button")

        # Handle project deletion request
        elif query.data.startswith("del_"):
            project_id = query.data.replace("del_", "")

            if project_id not in self.state.projects:
                await query.edit_message_text(f"❌ Project {project_id} not found.")
                return

            project_name = self.state.projects[project_id]

            # Show confirmation dialog
            keyboard = [
                [
                    InlineKeyboardButton(
                        "❌ Yes, delete", callback_data=f"confirm_del_{project_id}"
                    ),
                    InlineKeyboardButton("✅ Keep it", callback_data="cancel_del"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f'⚠️ Delete project "{project_name}"?\n\n'
                "This will permanently delete all notes in this project.",
                reply_markup=reply_markup,
            )

        # Handle deletion confirmation
        elif query.data.startswith("confirm_del_"):
            project_id = query.data.replace("confirm_del_", "")

            if project_id not in self.state.projects:
                await query.edit_message_text(f"❌ Project {project_id} not found.")
                return

            project_name = self.state.projects[project_id]

            # Remove project from state
            del self.state.projects[project_id]

            # If this was the active project, clear it
            if (
                user_id in self.state.active_sessions
                and self.state.active_sessions[user_id] == project_id
            ):
                del self.state.active_sessions[user_id]

            self.save_state()

            # Delete project directory
            import shutil

            for dir in self.config.projects_dir.iterdir():
                if dir.name.startswith(f"project-{project_id}-"):
                    shutil.rmtree(dir)
                    break

            await query.edit_message_text(f'🗑️ Deleted project "{project_name}"')
            logger.info(f"User {user_id} deleted project {project_id}")

        # Handle deletion cancellation
        elif query.data == "cancel_del":
            await query.edit_message_text(
                "✅ Deletion cancelled. Use /projects to see your projects."
            )

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        user_id = str(update.effective_user.id)
        message_id = str(update.message.message_id)

        # Check if message was already processed (for queue handling)
        if message_id in self.state.processed_messages:
            logger.info(f"Skipping already processed message {message_id}")
            return

        # Check if user has active project
        if user_id not in self.state.active_sessions:
            await update.message.reply_text("❌ No project selected. Use /pick <id> first.")
            return

        project_id = self.state.active_sessions[user_id]
        project_name = self.state.projects[project_id]

        # Send processing indicator
        processing_msg = await update.message.reply_text("📝 Processing...")

        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()

            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(
                suffix=".ogg", dir=self.config.audio_dir, delete=False
            ) as tmp_file:
                audio_path = Path(tmp_file.name)
                await voice_file.download_to_drive(audio_path)

            # Load Whisper if needed
            self.load_whisper()

            # Get user's language preference (default to English)
            user_lang = self.state.user_languages.get(user_id, "en")

            # Transcribe audio with user's selected language
            logger.info(f"Transcribing audio file: {audio_path} (language: {user_lang})")

            transcribe_params = {"fp16": False}  # Use FP32 for CPU
            if user_lang != "auto":
                transcribe_params["language"] = user_lang

            result = self.whisper_model.transcribe(str(audio_path), **transcribe_params)
            transcribed_text = result["text"].strip()
            detected_language = result.get("language", user_lang)
            logger.info(f"Language used: {detected_language}")

            # If Bulgarian, also get English translation
            translated_text = None
            if user_lang == "bg" or detected_language == "bg":
                logger.info("Getting English translation...")
                translate_result = self.whisper_model.transcribe(
                    str(audio_path),
                    language="bg",
                    task="translate",  # This translates to English
                    fp16=False,
                )
                translated_text = translate_result["text"].strip()
                logger.info("Translation complete")

            # Delete audio file
            audio_path.unlink()

            # Get timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Find project directory
            project_dir = None
            for dir in self.config.projects_dir.iterdir():
                if dir.name.startswith(f"project-{project_id}-"):
                    project_dir = dir
                    break

            if not project_dir:
                raise Exception(f"Project directory not found for ID {project_id}")

            # Append to notes file
            notes_file = project_dir / "notes.md"
            with open(notes_file, "a") as f:
                if translated_text:
                    # Write both Bulgarian and English
                    f.write(
                        f"## {timestamp}\n\n**Bulgarian:** {transcribed_text}\n\n**English:** {translated_text}\n\n"
                    )
                else:
                    # Write just the transcription
                    f.write(f"## {timestamp}\n\n{transcribed_text}\n\n")

            # Mark message as processed
            self.state.processed_messages.append(message_id)
            self.save_state()

            # Update confirmation message with word count
            word_count = len(transcribed_text.split())
            await processing_msg.edit_text(
                f'✅ Added to project "{project_name}" ({word_count} words)'
            )

            logger.info(f"Transcribed {word_count} words to project {project_id}")

        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            await processing_msg.edit_text(f"❌ Error: {str(e)}")

    async def process_queued_messages(self, application: Application):
        """Process messages that were sent while bot was offline"""
        logger.info("🔍 Checking for queued messages...")

        try:
            # Get updates since last processed
            updates = await application.bot.get_updates(
                offset=self.state.last_update_id + 1 if self.state.last_update_id else 0
            )

            if updates:
                logger.info(
                    f"📬 Found {len(updates)} messages in queue. Starting batch processing..."
                )

                for idx, update in enumerate(updates, 1):
                    logger.info(f"⏳ Processing queued message {idx}/{len(updates)}...")
                    # Update last processed ID
                    self.state.last_update_id = update.update_id

                    # Process voice messages
                    if update.message and update.message.voice:
                        # Temporarily set language to auto for queue processing
                        user_id = str(update.message.from_user.id)
                        original_lang = self.state.user_languages.get(user_id, "en")
                        self.state.user_languages[user_id] = "auto"

                        logger.info("🎤 Processing voice message from queue (auto-detect language)")
                        await self.handle_voice(update, None)

                        # Restore original language preference
                        self.state.user_languages[user_id] = original_lang
                    # Process commands
                    elif update.message and update.message.text:
                        text = update.message.text
                        if text.startswith("/"):
                            # Route to appropriate handler
                            if text.startswith("/start"):
                                await self.start_command(update, None)
                            elif text.startswith("/projects"):
                                await self.projects_command(update, None)
                            elif text.startswith("/new"):
                                # Parse args manually
                                parts = text.split(maxsplit=1)
                                if len(parts) > 1:
                                    context = type("obj", (object,), {"args": parts[1].split()})()
                                    await self.new_command(update, context)
                            elif text.startswith("/pick"):
                                parts = text.split()
                                if len(parts) > 1:
                                    context = type("obj", (object,), {"args": [parts[1]]})()
                                    await self.pick_command(update, context)
                            elif text.startswith("/status"):
                                await self.status_command(update, None)

                self.save_state()
                logger.info(f"✅ Finished processing {len(updates)} queued messages")
            else:
                logger.info("📭 No queued messages found")

        except Exception as e:
            logger.error(f"Error processing queued messages: {e}")

    async def post_init(self, application: Application) -> None:
        """Set up bot commands menu"""
        await application.bot.set_my_commands(
            [
                ("projects", "📁 List and select projects"),
                ("new", "➕ Create new project"),
                ("status", "📊 Show current status"),
                ("language", "🌐 Change language"),
            ]
        )
        logger.info("Bot commands menu set")

    def run(self):
        """Run the bot"""
        if not self.config.telegram_token:
            logger.error("TELEGRAM_TOKEN not set in .env file")
            return

        # Create application
        application = Application.builder().token(self.config.telegram_token).build()

        # Store bot instance in application context
        application.bot_data["bot_instance"] = self

        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("projects", self.projects_command))
        application.add_handler(CommandHandler("new", self.new_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("language", self.language_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))

        # Process queued messages on startup and set commands
        async def startup_callback(application: Application):
            bot_instance = application.bot_data["bot_instance"]
            await bot_instance.post_init(application)
            await bot_instance.process_queued_messages(application)

        application.post_init = startup_callback

        # Start bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    config = Config()
    bot = VoiceNotesBot(config)
    bot.run()


if __name__ == "__main__":
    main()
