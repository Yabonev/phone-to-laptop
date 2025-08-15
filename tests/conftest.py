"""Pytest configuration and fixtures"""
import pytest
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_config(temp_dir):
    """Provide test configuration"""
    return {
        'telegram_token': 'test_token_123',
        'whisper_model': 'tiny',
        'projects_dir': str(temp_dir / 'projects'),
        'audio_dir': str(temp_dir / 'audio'),
        'logs_dir': str(temp_dir / 'logs'),
        'state_file': str(temp_dir / 'state.json')
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
    """Create mock services with logger"""
    logger = logging.getLogger("test")
    return {
        'state': Mock(),
        'project': Mock(),
        'transcription': Mock(),
        'cleanup': Mock(),
        'logger': logger,
        'config': {}
    }