# 🎤 Phone to Laptop - Telegram Voice Transcription Bot

[![CI Pipeline](https://github.com/Yabonev/phone-to-laptop/actions/workflows/ci.yml/badge.svg)](https://github.com/Yabonev/phone-to-laptop/actions/workflows/ci.yml)
[![Docker Build](https://github.com/Yabonev/phone-to-laptop/actions/workflows/deploy.yml/badge.svg)](https://github.com/Yabonev/phone-to-laptop/actions/workflows/deploy.yml)

A Telegram bot that automatically transcribes voice messages and text messages from your phone to your laptop, organizing them into structured markdown projects. Built with clean architecture following SOLID principles.

## ✨ Features

### 🎙️ Voice Transcription
- **Automatic transcription** using OpenAI Whisper
- **Multi-language support** (English, Bulgarian with translation)
- **Offline message processing** - catches up when back online
- **Configurable quality** - Choose Whisper model size

### 📝 Text Message Logging
- **Automatic text logging** alongside voice messages
- **Message deduplication** - No duplicate entries
- **Smart filtering** - Excludes bot commands
- **Consistent formatting** - Clean markdown output

### 📁 Project Organization
- **Project-based organization** - Group messages by topic
- **Markdown export** - Clean, readable format
- **Timestamp tracking** - Never lose context
- **Message statistics** - Track activity and word counts

### 🔧 Architecture
- **Clean Architecture** - SOLID principles throughout
- **Pluggable Commands** - Easy to extend
- **Service Layer** - Proper separation of concerns
- **Dependency Injection** - Testable and maintainable

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yabonev/phone-to-laptop.git
   cd phone-to-laptop
   ```

2. **Install dependencies**
   ```bash
   uv sync --all-extras
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the bot**
   ```bash
   uv run python main.py
   ```

### Docker Setup (Recommended)

1. **Development**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Start development container
   docker-compose up bot
   ```

2. **Production**
   ```bash
   # Use production profile
   docker-compose --profile production up bot-production
   ```

## 📱 Usage

1. **Start the bot**: Send `/start` to see available commands
2. **Create a project**: `/new My Project Name`
3. **Select project**: `/projects` then pick from the list
4. **Send messages**: Voice messages and text are automatically logged
5. **Check status**: `/status` to see current project and statistics

### Commands
- `/start` - Welcome message and setup
- `/new <name>` - Create new project
- `/projects` - List/select projects
- `/status` - Current status and statistics
- `/language` - Change transcription language

## 📋 Output Format

Messages are organized in markdown files with clear distinction:

```markdown
# My Project Name

Voice notes transcriptions:

## 2025-01-26 14:30 [TEXT]

This is a text message I typed on my phone

## 2025-01-26 14:32 [VOICE]

This is a transcribed voice message

## 2025-01-26 14:35 [VOICE]

**Bulgarian:** Това е българско съобщение
**English:** This is a Bulgarian message
```

## 🛠️ Development

### Setup Development Environment
```bash
# Install with dev dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src
```

### Project Structure
```
phone-to-laptop/
├── src/
│   ├── commands/          # Bot commands (pluggable)
│   ├── core/             # Core bot logic and interfaces
│   └── services/         # Business logic services
├── tests/                # Comprehensive test suite
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD pipelines
```

### Adding New Commands

1. Create command class extending `Command`, `CallbackCommand`, or `VoiceCommand`
2. Register in `main.py`
3. Follow existing patterns and SOLID principles

Example:
```python
from src.core.command import Command

class MyCommand(Command):
    @property
    def name(self) -> str:
        return "mycommand"
    
    @property  
    def description(self) -> str:
        return "My custom command"
    
    async def execute(self, update, context):
        # Implementation using self.state, self.project_service, etc.
        pass
```

## 🔄 CI/CD Pipeline

### Automated Testing
- **Multi-Python versions** (3.11, 3.12)
- **Comprehensive test suite** (70+ tests)
- **Coverage reporting** via Codecov
- **Integration testing**

### Code Quality
- **Ruff** - Linting and formatting
- **MyPy** - Type checking  
- **Bandit** - Security scanning
- **Pre-commit hooks** available

### Deployment
- **Docker multi-stage builds**
- **GitHub Container Registry**
- **Automated releases**
- **Production environment support**

### Branch Protection
- ✅ All CI checks must pass
- ✅ No direct pushes to main
- ✅ Pull request workflow enforced

## 📊 Configuration

### Environment Variables
```bash
# Required
TELEGRAM_TOKEN=your_bot_token_here

# Optional (with defaults)
WHISPER_MODEL=large          # tiny, base, small, medium, large
PROJECTS_DIR=./projects      # Where to store projects
AUDIO_DIR=./audio           # Temp audio storage
LOGS_DIR=./logs             # Log files
```

### Whisper Models
- `tiny` - Fastest, lowest quality (~39 MB)
- `base` - Good balance (~74 MB)  
- `small` - Better quality (~244 MB)
- `medium` - High quality (~769 MB)
- `large` - Best quality (~1550 MB)

## 🧪 Testing

### Run Full Test Suite
```bash
uv run pytest -v
```

### Test Categories
- **Unit Tests** - Individual component testing
- **Integration Tests** - Service interaction testing  
- **End-to-End Tests** - Full workflow testing
- **Performance Tests** - Load and memory testing
- **Error Scenario Tests** - Edge case handling

### Test Coverage
```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## 📦 Deployment Options

### 1. Local Development
```bash
uv run python main.py
```

### 2. Docker Development
```bash
docker-compose up bot
```

### 3. Docker Production
```bash
docker-compose --profile production up bot-production
```

### 4. Container Registry
```bash
docker pull ghcr.io/yabonev/phone-to-laptop:latest
docker run -d --env-file .env ghcr.io/yabonev/phone-to-laptop:latest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the existing patterns
4. Add tests for new functionality
5. Ensure CI passes (`uv run pytest && uv run ruff check .`)
6. Create a Pull Request

### Development Workflow
1. **Branch protection** ensures quality
2. **All PRs require CI passing**
3. **Automated testing** on multiple Python versions
4. **Code review** process
5. **Automated deployment** after merge

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram API
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter

---

**⭐ Star this repo if you find it useful!**