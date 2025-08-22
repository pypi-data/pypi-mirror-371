class EnvFileNotFoundError(Exception):
    """Raised when .env file is missing."""
    pass


class EnvParsingError(Exception):
    """Raised when .env file cannot be parsed properly."""
    pass
