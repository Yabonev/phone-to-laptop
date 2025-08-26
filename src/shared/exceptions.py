"""Custom exceptions for the application."""


class BotException(Exception):
    """Base exception for bot-related errors."""
    pass


class ProjectException(BotException):
    """Exception for project-related errors."""
    pass


class TranscriptionException(BotException):
    """Exception for transcription-related errors."""
    pass


class ConfigurationException(BotException):
    """Exception for configuration-related errors."""
    pass