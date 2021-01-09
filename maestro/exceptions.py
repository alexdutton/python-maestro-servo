class MaestroException(Exception):
    """Base class for all Maestro-related exceptions."""


class NoMaestroAvailable(MaestroException):
    """Exception for when a Maestro device was requested, but none is available."""
