# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot that transcribes voice messages from phone to laptop, organizing them into markdown projects. Built with clean architecture following SOLID principles.

## Development Commands

### Run the bot
```bash
uv run python main.py
```

### Test individual components
```bash
# Test a specific command in isolation
uv run python -c "from src.commands.status import StatusCommand; print(StatusCommand.__doc__)"

# Check service initialization
uv run python -c "from src.services.container import ServiceContainer; sc = ServiceContainer({'state_file': 'test.json'})"
```

### Manage dependencies (uv only)
```bash
# Add new dependency
uv add package-name

# Sync environment
uv sync

# Run with uv
uv run python main.py
```

## Architecture

### Clean Architecture Layers
- **Entry Point** (`main.py`): Command registration and configuration
- **Core Layer** (`src/core/`): Bot orchestration, command interfaces, registry
- **Services Layer** (`src/services/`): Business logic (state, projects, transcription)
- **Commands Layer** (`src/commands/`): Individual command implementations

### SOLID Implementation
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Add new commands without modifying existing code
- **Liskov Substitution**: All commands implement the same interface
- **Interface Segregation**: Command, CallbackCommand, VoiceCommand interfaces
- **Dependency Inversion**: Commands depend on service abstractions

### Adding New Commands

1. Create command file in `src/commands/`:
```python
from src.core.command import Command

class MyCommand(Command):
    @property
    def name(self) -> str:
        return "mycommand"
    
    @property
    def description(self) -> str:
        return "Command description"
    
    async def execute(self, update, context):
        # Implementation using self.state, self.project_service, etc.
        pass
```

2. Register in `main.py`:
```python
from src.commands.my_command import MyCommand
bot.register_commands(..., MyCommand)
```

### Service Access in Commands
Commands automatically receive injected services:
- `self.state`: StateService for persistence
- `self.project_service`: ProjectService for file management  
- `self.transcription_service`: TranscriptionService for audio
- `self.config`: Configuration dictionary

## Key Files and Patterns

### Command Types
- **Basic Command**: Extends `Command`, handles text commands
- **CallbackCommand**: Extends `CallbackCommand`, handles button interactions
- **VoiceCommand**: Extends `VoiceCommand`, processes voice messages

### State Management
- State persisted in `state.json`
- Tracks: projects, active project, processed messages, user preferences
- Auto-saves on every change

### Project Structure
```
projects/
└── project-XXX-name/
    └── notes.md  # Transcribed voice messages with timestamps
```

### Audio Processing
- Whisper model for transcription (configurable: tiny, base, small, medium, large)
- Audio files temporarily stored in `audio/` then deleted after processing
- Supports .ogg format from Telegram

## Testing Approach

Tests are documented in `tests/` as markdown test plans with Arrange/Act/Assert structure. Run verification:

```bash
# Verify command registration works
uv run python -c "from src.core.bot import VoiceNotesBot; bot = VoiceNotesBot({'telegram_token': 'test'}); print('Commands registered:', len(bot.registry.commands))"

# Test service isolation
uv run python -c "from src.services.state import StateService; s = StateService('test.json'); s.add_project('001', 'Test'); print(s.get_projects())"
```

## Environment Configuration

Required `.env` file (copy from `.env.example`):
- `TELEGRAM_TOKEN`: Bot token from BotFather
- `WHISPER_MODEL`: Model size (tiny/base/small/medium/large)
- `PROJECTS_DIR`: Where to store project files
- `AUDIO_DIR`: Temporary audio storage
- `LOGS_DIR`: Log file location

## macOS Auto-start

LaunchAgent service managed via:
```bash
# Start/stop/restart
launchctl start com.user.telegram-voice-bot
launchctl stop com.user.telegram-voice-bot

# View logs
tail -f logs/bot.log
tail -f logs/launchd.err.log
```

## Bot Commands

- `/start` - Welcome message and menu
- `/new <name>` - Create new project
- `/projects` - List all projects with buttons
- `/pick <id>` - Select active project
- `/status` - Show current status
- `/language <code>` - Set transcription language
- Voice messages - Automatically transcribed to active project

## Dependencies

Core packages (managed via uv/pyproject.toml):
- `python-telegram-bot`: Telegram API interface
- `openai-whisper`: Voice transcription
- `pydantic`: Data validation
- `python-dotenv`: Environment configuration
- `rich`: Enhanced logging output