import os

def cast_value(value: str):
    """Auto type casting for environment values."""
    val = value.strip()

    # Boolean casting
    if val.lower() in ("true", "yes", "1", "on"):
        return True
    if val.lower() in ("false", "no", "0", "off"):
        return False

    # None casting
    if val.lower() in ("none", "null", "nil"):
        return None

    # Integer casting
    if val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
        return int(val)

    # Float casting
    try:
        return float(val)
    except ValueError:
        pass

    # Default string
    return val


def parse_env_file(filepath: str):
    """Parse .env file and return dictionary of variables."""
    env_dict = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip().strip('"').strip("'")

            env_dict[key] = cast_value(value)

    return env_dict
