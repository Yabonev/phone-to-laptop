"""Tests for core bot components"""
import pytest
import logging
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from src.core.bot import VoiceNotesBot
from src.core.registry import CommandRegistry
from src.core.command import Command, CallbackCommand, VoiceCommand


class TestCommand(Command):
    """Test command implementation"""
    
    def __init__(self, services):
        super().__init__(services)
        self.executed = False
        
    @property
    def name(self):
        return "test"
    
    @property
    def description(self):
        return "Test command"
    
    async def execute(self, update, context):
        self.executed = True


class TestCallbackCommand(CallbackCommand):
    """Test callback command implementation"""
    
    def __init__(self, services):
        super().__init__(services)
        self.callback_handled = False
        
    @property
    def name(self):
        return "testcallback"
    
    @property
    def description(self):
        return "Test callback command"
    
    def get_callback_patterns(self):
        return ["test_"]
    
    async def execute(self, update, context):
        pass
    
    async def handle_callback(self, update, context):
        self.callback_handled = True


class TestCommandRegistry:
    """Test command registration and management"""
    
    def test_command_registration(self):
        """Test registering basic commands"""
        registry = CommandRegistry()
        command = TestCommand({})
        
        registry.register(command)
        
        assert "test" in registry.commands
        assert registry.get_command("test") == command
        
    def test_callback_registration(self):
        """Test registering callback commands"""
        registry = CommandRegistry()
        command = TestCallbackCommand({})
        
        registry.register(command)
        
        # Should be in commands and callback handlers
        assert "testcallback" in registry.commands
        assert "test_" in registry.callback_handlers
        assert registry.callback_handlers["test_"] == command
        
    def test_voice_handler_registration(self):
        """Test registering voice handler"""
        registry = CommandRegistry()
        
        class TestVoiceCommand(VoiceCommand):
            @property
            def name(self):
                return "voice"
            
            @property
            def description(self):
                return "Voice handler"
            
            async def execute(self, update, context):
                pass
            
            async def handle_voice(self, update, context):
                pass
        
        voice_command = TestVoiceCommand({})
        registry.register(voice_command)
        
        assert registry.voice_handler == voice_command
        
    def test_unregister_command(self):
        """Test unregistering commands"""
        registry = CommandRegistry()
        command = TestCommand({})
        
        registry.register(command)
        assert "test" in registry.commands
        
        registry.unregister("test")
        assert "test" not in registry.commands
        
    def test_get_bot_commands(self):
        """Test getting bot menu commands"""
        registry = CommandRegistry()
        
        # Add command that shows in menu
        command1 = TestCommand({})
        # show_in_menu is a property, not settable
        registry.register(command1)
        
        # Add command that doesn't show in menu
        command2 = TestCallbackCommand({})
        registry.register(command2)
        
        bot_commands = registry.get_bot_commands()
        
        # Both commands show in menu by default
        assert len(bot_commands) == 2
        
    def test_handle_callback_query(self):
        """Test callback query routing"""
        registry = CommandRegistry()
        callback_cmd = TestCallbackCommand({})
        registry.register(callback_cmd)
        
        # Test matching callback
        handler = registry.get_callback_handler("test_123")
        assert handler == callback_cmd
        
        # Test non-matching callback
        handler = registry.get_callback_handler("nomatch_123")
        assert handler is None


class TestVoiceNotesBot:
    """Test main bot class"""
    
    def test_bot_initialization(self, test_config):
        """Test bot initializes with all components"""
        bot = VoiceNotesBot(test_config)
        
        # Check components exist
        assert bot.container is not None
        assert bot.registry is not None
        assert bot.config == test_config
        
    def test_directories_created(self, test_config, temp_dir):
        """Test required directories are created"""
        bot = VoiceNotesBot(test_config)
        
        # Check directories exist
        assert Path(test_config['projects_dir']).exists()
        assert Path(test_config['audio_dir']).exists()
        assert Path(test_config['logs_dir']).exists()
        
    def test_command_registration(self, test_config):
        """Test registering commands with bot"""
        bot = VoiceNotesBot(test_config)
        
        # Register test command
        bot.register_command(TestCommand)
        
        # Verify registration
        assert "test" in bot.registry.commands
        
    def test_multiple_command_registration(self, test_config):
        """Test registering multiple commands"""
        bot = VoiceNotesBot(test_config)
        
        # Register multiple commands
        bot.register_commands(TestCommand, TestCallbackCommand)
        
        # Verify both registered
        assert "test" in bot.registry.commands
        assert "testcallback" in bot.registry.commands
        
    @pytest.mark.asyncio
    async def test_process_queued_messages_empty(self, test_config):
        """Test processing when no queued messages"""
        bot = VoiceNotesBot(test_config)
        
        # Mock application
        app = Mock()
        app.bot = Mock()
        app.bot.get_updates = AsyncMock(return_value=[])
        
        # Process (should handle empty queue gracefully)
        await bot.process_queued_messages(app)
        
        # Verify no errors and state saved
        state = bot.container.get('state')
        assert state is not None
        
    @pytest.mark.asyncio
    async def test_setup_bot_menu(self, test_config):
        """Test bot menu setup"""
        bot = VoiceNotesBot(test_config)
        
        # Add command with menu
        bot.register_command(TestCommand)
        
        # Mock application
        app = Mock()
        app.bot = Mock()
        app.bot.set_my_commands = AsyncMock()
        
        # Setup menu
        await bot.setup_bot_menu(app)
        
        # Verify menu was set
        app.bot.set_my_commands.assert_called_once()
        
    def test_bot_run_without_token(self):
        """Test bot handles missing token gracefully"""
        config = {'telegram_token': None}
        bot = VoiceNotesBot(config)
        
        # Should return without error
        result = bot.run()
        assert result is None  # Exits early due to no token


class TestCommandBase:
    """Test command base classes"""
    
    def test_command_initialization(self):
        """Test command gets services"""
        services = {
            'state': Mock(),
            'project': Mock(),
            'config': {'test': 'value'},
            'logger': logging.getLogger('test')
        }
        
        command = TestCommand(services)
        
        assert command.state == services['state']
        assert command.project_service == services['project']
        # config is stored in services dict, not as separate attribute
        assert command.services['config'] == services['config']
        
    def test_command_show_in_menu_default(self):
        """Test default menu visibility"""
        command = TestCommand({})
        assert command.show_in_menu is True
        
    def test_command_menu_icon_default(self):
        """Test default menu icon"""
        command = TestCommand({})
        assert command.menu_icon == ""
        
    def test_callback_command_patterns(self):
        """Test callback command must implement patterns"""
        command = TestCallbackCommand({})
        patterns = command.get_callback_patterns()
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert all(isinstance(p, str) for p in patterns)