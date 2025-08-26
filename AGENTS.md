# Agent Guidelines for phone-to-laptop

## Commands
```bash
uv run python main.py          # Run the bot
uv run pytest tests/test_*.py -k test_name  # Run single test
uv run pytest -m unit          # Run unit tests only
uv run ruff check src/ --fix   # Lint with autofix
uv run ruff format src/        # Format code
uv run mypy src/               # Type checking
```

## Project Structure
- `src/bot/` - Telegram bot commands and handlers
- `src/core/` - Business logic and domain models  
- `src/infrastructure/` - External dependencies (storage, transcription)
- `tests/test_*` - Tests organized by layer

## Code Style
- **Python 3.11+**, line length 100, double quotes for strings
- **Commands**: Extend from `src.bot.commands.base`
- **Services**: Injected via constructor
- **Async/await**: All bot handlers must be async
- **Testing**: Mark with @pytest.mark.unit/integration