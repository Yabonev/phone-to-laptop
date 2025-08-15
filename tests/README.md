# Phone-to-Laptop Bot Test Suite

This directory contains comprehensive tests for the Phone-to-Laptop Telegram bot.

## Test Files

### 1. `executable_tests.md`
Complete test suite with copy-paste executable code blocks that any LLM can run. Each test includes:
- Setup code
- Execution commands
- Expected output
- Cleanup steps

### 2. `run_tests.py`
Automated test runner that executes all tests with a single command:
```bash
uv run python run_tests.py
```

Add `--verbose` for detailed error output:
```bash
uv run python run_tests.py --verbose
```

### 3. Legacy Test Files
- `test_architecture.md` - Architecture and SOLID principles tests
- `test_cleanup.md` - Cleanup service specific tests
- `test_simple_language.md` - Language selection tests
- `test_auto_detect_limit.md` - Auto-detect feature tests (deprecated)

## Test Coverage

The test suite covers:

1. **Service Layer**
   - Service container initialization
   - State persistence and loading
   - Project management (create, archive, stats)
   - Cleanup service (audio files, log rotation)
   - Transcription service setup

2. **Core Components**
   - Command registration system
   - Bot initialization
   - Directory creation
   - Configuration handling

3. **Business Logic**
   - Language settings (English/Bulgarian)
   - Project notes with translations
   - Message processing state
   - File retention policies

## Running Tests

### Quick Test
```bash
# Run all tests automatically
uv run python run_tests.py
```

### Manual Testing
For any specific test from `executable_tests.md`:
1. Copy the code block
2. Paste into terminal
3. Compare output with expected results

### Continuous Testing
Tests run automatically on bot startup:
- Log rotation (if > 1000 lines)
- Old audio file cleanup (> 7 days)

## Test Requirements

- Python 3.11+
- `uv` package manager
- All project dependencies installed via `uv sync`
- No Telegram token needed (tests use mocks)

## Adding New Tests

To add a new test:

1. Add test method to `run_tests.py`:
```python
def test_new_feature(self):
    """Test description"""
    # Test implementation
    assert condition, "Error message"
```

2. Register in `run_all()` method:
```python
self.run_test("New Feature", self.test_new_feature)
```

3. Document in `executable_tests.md` with:
   - Setup commands
   - Expected output
   - Cleanup steps

## Test Principles

All tests follow these principles:
1. **Independent** - Each test can run standalone
2. **Repeatable** - Same results every time
3. **Self-cleaning** - Remove all test artifacts
4. **Executable** - Any LLM can run them
5. **Verifiable** - Clear pass/fail criteria

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

Use in CI/CD:
```bash
uv run python run_tests.py || exit 1
```