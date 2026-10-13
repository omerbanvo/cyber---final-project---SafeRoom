class SafeRoomError(Exception):
    """Base class for all project errors."""

class ConfigError(SafeRoomError):
    """Problem with the config file."""

    