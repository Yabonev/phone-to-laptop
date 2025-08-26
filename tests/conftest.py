"""Pytest configuration and fixtures for real functionality testing"""

import logging
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from src.core.services.container import ServiceContainer
from src.infrastructure.transcription.whisper_adapter import TranscriptionService
from tests.audio_helpers import AudioGenerator, create_test_audio_files


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_config(temp_dir):
    """Provide test configuration for real service testing"""
    return {
        "telegram_token": "test_token_123",
        "whisper_model": "tiny",  # Fast model for testing
        "projects_dir": str(temp_dir / "projects"),
        "audio_dir": str(temp_dir / "audio"),
        "logs_dir": str(temp_dir / "logs"),
        "state_file": str(temp_dir / "state.json"),
    }


@pytest.fixture
def mock_telegram_update():
    """Create a mock Telegram update"""
    update = Mock()
    update.message = Mock()
    update.message.message_id = 123
    update.message.text = "/test"
    update.message.reply_text = AsyncMock()
    update.effective_user = Mock()
    update.effective_user.id = 12345
    return update


@pytest.fixture
def mock_telegram_context():
    """Create a mock Telegram context"""
    context = Mock()
    context.args = []
    return context


@pytest.fixture
def mock_services():
    """Create mock services with logger - USE SPARINGLY, prefer real_services"""
    logger = logging.getLogger("test")
    return {
        "state": Mock(),
        "project": Mock(),
        "transcription": Mock(),
        "cleanup": Mock(),
        "logger": logger,
        "config": {},
    }


@pytest.fixture
def real_services(test_config) -> ServiceContainer:
    """Create REAL service container for integration testing"""
    # Use tiny model for fast testing
    config = test_config.copy()
    config["whisper_model"] = "tiny"

    container = ServiceContainer(config)
    return container


@pytest.fixture
def audio_generator() -> AudioGenerator:
    """Audio generator for creating test audio files"""
    return AudioGenerator()


@pytest.fixture
def test_audio_files(temp_dir) -> dict[str, list[Path]]:
    """Pre-generated test audio files for transcription testing"""
    audio_dir = temp_dir / "test_audio"
    return create_test_audio_files(audio_dir, durations=[1.0, 2.0])


@pytest.fixture(scope="session")
def shared_whisper_model():
    """Shared Whisper model for tests to avoid repeated loading"""
    import whisper

    model = whisper.load_model("tiny")
    return model


@pytest.fixture
def real_transcription_service(temp_dir, shared_whisper_model) -> TranscriptionService:
    """Real transcription service with pre-loaded model for faster testing"""
    service = TranscriptionService(model_name="tiny", audio_dir=temp_dir / "audio")
    # Pre-load the shared model to avoid repeated loading
    service.model = shared_whisper_model
    return service


@pytest.fixture
def performance_timer():
    """Timer for performance testing"""

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()
            return self.duration

        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return Timer()


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (may take several seconds)")
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (use real services)"
    )
    config.addinivalue_line("markers", "transcription: marks tests that use real Whisper model")
    config.addinivalue_line("markers", "performance: marks tests that measure performance")
