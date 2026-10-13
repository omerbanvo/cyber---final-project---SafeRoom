class SafeRoomError(Exception):
    """Base class for all project errors."""

class ConfigError(SafeRoomError):
    """Problem with the config file."""

class SafeRoomError(Exception):
    """Base class for all project errors."""


class ConfigError(SafeRoomError):
    """Problem with the config file."""


class FrameTooLarge(SafeRoomError):
    """Declared frame length is bigger than the allowed maximum."""


class InvalidFrame(SafeRoomError):
    """Frame is malformed (for example, length is 0)."""


class ConnectionClosed(SafeRoomError):
    """The other side closed the connection."""


class ProtocolError(SafeRoomError):
    """message is not valid according to the protocol"""
