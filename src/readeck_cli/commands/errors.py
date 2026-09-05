class CommandError(Exception):
    """Raised when a command fails to complete.

    This is the only error type callers outside `commands/` need to know
    about — each command translates infrastructure-level failures into
    this before they cross the package boundary.
    """
