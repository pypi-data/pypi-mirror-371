import os
import pytest
from atikin_env import load_env, get
from atikin_env.exceptions import EnvFileNotFoundError


def test_load_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("NAME=AtikinVerse\nAGE=25\nDEBUG=true\n")

    load_env(str(env_file))
    assert get("NAME") == "AtikinVerse"
    assert get("AGE") == 25
    assert get("DEBUG") is True


def test_missing_env_file():
    try:
        load_env("missing.env")
    except EnvFileNotFoundError:
        assert True
