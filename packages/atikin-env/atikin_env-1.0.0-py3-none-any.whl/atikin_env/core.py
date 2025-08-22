import os
import sys
from pathlib import Path

# Add src folder to sys.path (important for pytest & local imports)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from .parser import parse_env_file
from .exceptions import EnvFileNotFoundError


_ENV_CACHE = {}


def load_env(filepath: str = ".env", override: bool = False):
    """
    Load environment variables from a .env file into os.environ
    """
    path = Path(filepath)

    if not path.exists():
        raise EnvFileNotFoundError(f".env file not found at {filepath}")

    env_dict = parse_env_file(str(path))

    for key, value in env_dict.items():
        if override or key not in os.environ:
            os.environ[key] = str(value)
            _ENV_CACHE[key] = value

    return _ENV_CACHE


def get(key: str, default=None):
    """
    Get an environment variable with auto type casting.
    """
    if key in _ENV_CACHE:
        return _ENV_CACHE[key]

    value = os.getenv(key, default)
    return value
