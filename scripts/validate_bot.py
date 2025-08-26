#!/usr/bin/env python
"""
Simple validation to ensure bot structure is correct.
This catches common AI mistakes when modifying the code.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_required_files():
    """Check that essential files exist."""
    required = [
        "main.py",
        "src/core/bot.py",
        "src/core/command.py",
        "src/services/state.py",
        "src/commands/start.py",
        ".env.example",
    ]

    missing = []
    for file in required:
        if not Path(file).exists():
            missing.append(file)

    return missing


def check_command_registration():
    """Ensure all commands can be imported."""
    errors = []

    try:
        from src.commands.projects import ProjectsCommand  # noqa: F401
        from src.commands.start import StartCommand  # noqa: F401
        from src.commands.status import StatusCommand  # noqa: F401
        from src.commands.text import TextMessageHandler  # noqa: F401
        from src.commands.voice import VoiceMessageHandler  # noqa: F401
    except ImportError as e:
        errors.append(f"Cannot import commands: {e}")

    return errors


def check_services():
    """Ensure services can be initialized."""
    errors = []

    try:
        from src.services.container import ServiceContainer

        # Try to create container with test config
        config = {
            "state_file": "test.json",
            "projects_dir": "test_projects",
            "audio_dir": "test_audio",
            "whisper_model": "tiny",
        }
        ServiceContainer(config)  # Just test initialization
    except Exception as e:
        errors.append(f"Cannot initialize services: {e}")

    return errors


def check_clean_architecture():
    """Basic architecture checks."""
    violations = []

    # Commands shouldn't import from main
    commands_dir = Path("src/commands")
    if commands_dir.exists():
        for py_file in commands_dir.glob("*.py"):
            with open(py_file) as f:
                content = f.read()
                if "from main import" in content or "import main" in content:
                    violations.append(f"{py_file.name}: Commands shouldn't import from main.py")

    # Services shouldn't import from commands
    services_dir = Path("src/services")
    if services_dir.exists():
        for py_file in services_dir.glob("*.py"):
            with open(py_file) as f:
                content = f.read()
                if "from src.commands" in content:
                    violations.append(f"{py_file.name}: Services shouldn't import from commands")

    return violations


def main():
    """Run all validations."""
    print("🤖 Validating Bot Structure...")
    print("-" * 40)

    all_errors = []

    # Check files
    print("📁 Checking required files...")
    missing = check_required_files()
    if missing:
        for file in missing:
            print(f"  ❌ Missing: {file}")
            all_errors.append(f"Missing file: {file}")
    else:
        print("  ✅ All required files present")

    # Check imports
    print("\n📦 Checking command imports...")
    import_errors = check_command_registration()
    if import_errors:
        for error in import_errors:
            print(f"  ❌ {error}")
            all_errors.append(error)
    else:
        print("  ✅ All commands can be imported")

    # Check services
    print("\n⚙️  Checking services...")
    service_errors = check_services()
    if service_errors:
        for error in service_errors:
            print(f"  ❌ {error}")
            all_errors.append(error)
    else:
        print("  ✅ Services initialize correctly")

    # Check architecture
    print("\n🏗️  Checking architecture...")
    violations = check_clean_architecture()
    if violations:
        for violation in violations:
            print(f"  ⚠️  {violation}")
            # Don't add to errors - just warnings
    else:
        print("  ✅ Architecture rules followed")

    # Summary
    print("\n" + "-" * 40)
    if all_errors:
        print(f"❌ Validation failed with {len(all_errors)} error(s)")
        sys.exit(1)
    else:
        print("✅ Bot structure validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
