# Executable Tests for Phone-to-Laptop Bot

These tests are designed to be executed by any LLM with file system and bash access.

## Test 1: Service Initialization

```bash
# Execute this Python code to test service initialization
cat > test_services.py << 'EOF'
from src.services.container import ServiceContainer
from pathlib import Path

# Test service container creation
config = {
    'state_file': 'test_state.json',
    'projects_dir': './test_projects',
    'audio_dir': './test_audio',
    'logs_dir': './test_logs',
    'whisper_model': 'tiny'
}

container = ServiceContainer(config)

# Verify all services exist
services = ['state', 'project', 'transcription', 'cleanup', 'config']
for service_name in services:
    service = container.get(service_name)
    assert service is not None, f"Service {service_name} not found"
    print(f"✓ Service {service_name} initialized")

# Cleanup test files
Path('test_state.json').unlink(missing_ok=True)
print("\n✅ All services initialized correctly")
EOF

uv run python test_services.py
rm test_services.py
```

**Expected Output:**
```
✓ Service state initialized
✓ Service project initialized
✓ Service transcription initialized
✓ Service cleanup initialized
✓ Service config initialized

✅ All services initialized correctly
```

## Test 2: State Service Persistence

```bash
# Execute this to test state persistence
cat > test_state.py << 'EOF'
from src.services.state import StateService
from pathlib import Path
import json

# Create state service
state = StateService(Path("test_state.json"))

# Add test data
state.add_project("001", "Test Project")
state.set_active_project("001")
state.set_language("bg")
state.mark_message_processed("msg_123")

# Verify data was saved
with open("test_state.json", "r") as f:
    saved_data = json.load(f)
    
assert saved_data["active_project"] == "001", "Active project not saved"
assert saved_data["language"] == "bg", "Language not saved"
assert "001" in saved_data["projects"], "Project not saved"
assert "msg_123" in saved_data["processed_messages"], "Message not marked"

print("✓ State saved correctly")

# Test loading
state2 = StateService(Path("test_state.json"))
assert state2.get_active_project() == "001", "State not loaded correctly"
assert state2.get_language() == "bg", "Language not loaded correctly"

print("✓ State loaded correctly")

# Cleanup
Path("test_state.json").unlink()
print("\n✅ State persistence test passed")
EOF

uv run python test_state.py
rm test_state.py
```

**Expected Output:**
```
✓ State saved correctly
✓ State loaded correctly

✅ State persistence test passed
```

## Test 3: Project Management

```bash
# Execute this to test project creation and management
cat > test_project.py << 'EOF'
from src.services.project import ProjectService
from pathlib import Path
import shutil

# Create project service
projects_dir = Path("./test_projects")
service = ProjectService(projects_dir)

# Create a project
project_id = service.create_project("Test Project", {})
assert project_id == "001", f"Expected ID 001, got {project_id}"
print(f"✓ Created project with ID: {project_id}")

# Add notes
success = service.add_note("001", "Test note", "Test translation")
assert success, "Failed to add note"
print("✓ Added note to project")

# Verify files exist
project_dir = service.get_project_dir("001")
assert project_dir.exists(), "Project directory not created"
notes_file = project_dir / "notes.md"
assert notes_file.exists(), "Notes file not created"
print("✓ Project files created correctly")

# Get stats
messages, words = service.get_project_stats("001")
assert messages > 0, "No messages counted"
assert words > 0, "No words counted"
print(f"✓ Stats: {messages} messages, {words} words")

# Archive project
archived = service.archive_project("001")
assert archived, "Failed to archive"
assert not project_dir.exists(), "Original directory still exists"
print("✓ Project archived successfully")

# Cleanup
shutil.rmtree(projects_dir.parent / "archive", ignore_errors=True)
shutil.rmtree(projects_dir, ignore_errors=True)
print("\n✅ Project management test passed")
EOF

uv run python test_project.py
rm test_project.py
```

**Expected Output:**
```
✓ Created project with ID: 001
✓ Added note to project
✓ Project files created correctly
✓ Stats: 1 messages, 4 words
✓ Project archived successfully

✅ Project management test passed
```

## Test 4: Language Settings

```bash
# Execute this to test language handling
cat > test_language.py << 'EOF'
from src.services.state import StateService
from pathlib import Path

state = StateService(Path("test_state.json"))

# Test default language
default_lang = state.get_language()
assert default_lang == "en", f"Default should be 'en', got {default_lang}"
print(f"✓ Default language: {default_lang}")

# Test setting Bulgarian
state.set_language("bg")
assert state.get_language() == "bg", "Failed to set Bulgarian"
print("✓ Set language to Bulgarian")

# Test persistence
state2 = StateService(Path("test_state.json"))
assert state2.get_language() == "bg", "Language not persisted"
print("✓ Language setting persisted")

# Cleanup
Path("test_state.json").unlink()
print("\n✅ Language settings test passed")
EOF

uv run python test_language.py
rm test_language.py
```

**Expected Output:**
```
✓ Default language: en
✓ Set language to Bulgarian
✓ Language setting persisted

✅ Language settings test passed
```

## Test 5: Cleanup Service

```bash
# Execute this to test cleanup functionality
cat > test_cleanup.py << 'EOF'
from src.services.cleanup import CleanupService
from pathlib import Path
from datetime import datetime, timedelta
import time

# Setup directories
audio_dir = Path("./test_audio")
logs_dir = Path("./test_logs")
audio_dir.mkdir(exist_ok=True)
logs_dir.mkdir(exist_ok=True)

# Create cleanup service
cleanup = CleanupService(audio_dir, logs_dir)

# Test 1: Audio file cleanup
# Create old and new audio files
old_file = audio_dir / "old.ogg"
new_file = audio_dir / "new.ogg"
old_file.touch()
new_file.touch()

# Make old file 8 days old
import os
old_time = (datetime.now() - timedelta(days=8)).timestamp()
os.utime(old_file, (old_time, old_time))

# Run cleanup
deleted = cleanup.cleanup_old_audio_files()
assert deleted == 1, f"Expected 1 file deleted, got {deleted}"
assert not old_file.exists(), "Old file not deleted"
assert new_file.exists(), "New file was deleted"
print("✓ Old audio files cleaned up")

# Test 2: Log rotation
log_file = logs_dir / "bot.log"
with open(log_file, "w") as f:
    for i in range(1500):
        f.write(f"Line {i}\\n")

rotated = cleanup.rotate_log_file("bot.log")
assert rotated, "Log not rotated"

with open(log_file, "r") as f:
    lines = f.readlines()
    assert len(lines) == 1000, f"Expected 1000 lines, got {len(lines)}"
    assert lines[0].strip() == "Line 500", "Wrong lines kept"
print("✓ Log file rotated correctly")

# Cleanup
import shutil
shutil.rmtree(audio_dir)
shutil.rmtree(logs_dir)
print("\n✅ Cleanup service test passed")
EOF

uv run python test_cleanup.py
rm test_cleanup.py
```

**Expected Output:**
```
✓ Old audio files cleaned up
✓ Log file rotated correctly

✅ Cleanup service test passed
```

## Test 6: Command Registration

```bash
# Execute this to test command registration
cat > test_commands.py << 'EOF'
from src.core.registry import CommandRegistry
from src.core.command import Command

# Create test command
class TestCommand(Command):
    @property
    def name(self):
        return "test"
    
    @property
    def description(self):
        return "Test command"
    
    async def execute(self, update, context):
        pass

# Test registration
registry = CommandRegistry()
registry.register(TestCommand, {})

# Verify registration
assert registry.has_command("test"), "Command not registered"
cmd = registry.get_command("test")
assert cmd is not None, "Command not retrievable"
assert isinstance(cmd, TestCommand), "Wrong command type"
print("✓ Command registered successfully")

# Test menu commands
menu_cmds = registry.get_bot_commands()
assert len(menu_cmds) > 0, "No menu commands"
print(f"✓ Menu has {len(menu_cmds)} commands")

print("\n✅ Command registration test passed")
EOF

uv run python test_commands.py
rm test_commands.py
```

**Expected Output:**
```
✓ Command registered successfully
✓ Menu has 1 commands

✅ Command registration test passed
```

## Test 7: Full Integration Test

```bash
# This tests that all components work together
cat > test_integration.py << 'EOF'
from src.core.bot import VoiceNotesBot
from pathlib import Path
import shutil

# Create test config
config = {
    'telegram_token': 'test_token',
    'whisper_model': 'tiny',
    'projects_dir': './test_projects',
    'audio_dir': './test_audio',
    'logs_dir': './test_logs',
    'state_file': 'test_state.json'
}

# Create bot
bot = VoiceNotesBot(config)
print("✓ Bot initialized")

# Verify services exist
assert bot.container.get('state') is not None, "State service missing"
assert bot.container.get('project') is not None, "Project service missing"
assert bot.container.get('cleanup') is not None, "Cleanup service missing"
print("✓ All services available")

# Verify directories created
assert Path('./test_projects').exists(), "Projects dir not created"
assert Path('./test_audio').exists(), "Audio dir not created"
assert Path('./test_logs').exists(), "Logs dir not created"
print("✓ Directories created")

# Cleanup
shutil.rmtree('./test_projects', ignore_errors=True)
shutil.rmtree('./test_audio', ignore_errors=True)
shutil.rmtree('./test_logs', ignore_errors=True)
Path('test_state.json').unlink(missing_ok=True)

print("\n✅ Integration test passed")
EOF

uv run python test_integration.py
rm test_integration.py
```

**Expected Output:**
```
✓ Bot initialized
✓ All services available
✓ Directories created

✅ Integration test passed
```

## Run All Tests

To run all tests at once:

```bash
# Save this as run_all_tests.sh
#!/bin/bash

echo "Running Phone-to-Laptop Bot Tests..."
echo "====================================="

# Test counter
PASSED=0
FAILED=0

# Function to run a test
run_test() {
    echo -e "\n📝 Running: $1"
    if eval "$2"; then
        echo "✅ PASSED: $1"
        ((PASSED++))
    else
        echo "❌ FAILED: $1"
        ((FAILED++))
    fi
}

# Run each test
run_test "Service Initialization" "uv run python -c 'from src.services.container import ServiceContainer; ServiceContainer({})'"
run_test "State Persistence" "uv run python -c 'from src.services.state import StateService; from pathlib import Path; s = StateService(Path(\"t.json\")); s.set_language(\"en\"); Path(\"t.json\").unlink()'"
run_test "Project Management" "uv run python -c 'from src.services.project import ProjectService; from pathlib import Path; ProjectService(Path(\"./tp\"))'"
run_test "Cleanup Service" "uv run python -c 'from src.services.cleanup import CleanupService; CleanupService()'"
run_test "Command Registry" "uv run python -c 'from src.core.registry import CommandRegistry; CommandRegistry()'"

# Summary
echo -e "\n====================================="
echo "Test Results:"
echo "  ✅ Passed: $PASSED"
echo "  ❌ Failed: $FAILED"
echo "====================================="

# Cleanup any test artifacts
rm -rf test_* tp t.json 2>/dev/null

exit $FAILED
```

## Notes for LLM Execution

1. **Prerequisites**: Ensure you're in the project directory and have `uv` installed
2. **Each test is independent**: Can be run in any order
3. **Cleanup included**: Each test cleans up after itself
4. **Expected outputs provided**: Compare actual output with expected
5. **Error handling**: Tests will fail with assertion errors if something is wrong
6. **No bot token needed**: Tests use mock tokens where needed