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

## Code Style
- **Python 3.11+**, line length 100, double quotes for strings
- **Imports**: Group stdlib/third-party/local, use `from typing import` for types
- **SOLID**: Each class has single responsibility; add commands in main.py only
- **Commands**: Extend `Command`/`CallbackCommand`/`VoiceCommand` from `src.core.command`
- **Services**: Injected via constructor, access as `self.state`, `self.project_service`, etc.
- **Async/await**: All bot handlers and command methods must be async
- **Error handling**: Let exceptions bubble up, bot handles gracefully
- **Testing**: Fixtures in conftest.py, mark tests with @pytest.mark.unit/integration
- **No hardcoded secrets**: Use .env file, check with pre-commit hooks