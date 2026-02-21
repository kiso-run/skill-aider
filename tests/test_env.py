"""Tests for build_env()."""

import os
import pwd
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from run import build_env


API_KEY = "sk-test-1234"


def test_openrouter_provider():
    env = build_env(API_KEY, "openrouter", {})
    assert env.get("OPENROUTER_API_KEY") == API_KEY


def test_openai_provider():
    env = build_env(API_KEY, "openai", {})
    assert env.get("OPENAI_API_KEY") == API_KEY


def test_anthropic_provider():
    env = build_env(API_KEY, "anthropic", {})
    assert env.get("ANTHROPIC_API_KEY") == API_KEY


def test_deepseek_provider():
    env = build_env(API_KEY, "deepseek", {})
    assert env.get("DEEPSEEK_API_KEY") == API_KEY


def test_unknown_provider_falls_back_to_openai():
    env = build_env(API_KEY, "mycloud", {})
    assert env.get("OPENAI_API_KEY") == API_KEY


def test_home_always_present():
    env = build_env(API_KEY, "openrouter", {})
    assert "HOME" in env
    # HOME must come from pwd, not from the process environment
    expected_home = pwd.getpwuid(os.getuid()).pw_dir
    assert env["HOME"] == expected_home


def test_api_base_sets_openai_api_base():
    config = {"api_base": "https://proxy.example.com/v1"}
    env = build_env(API_KEY, "openrouter", config)
    assert env.get("OPENAI_API_BASE") == "https://proxy.example.com/v1"


def test_no_api_base_not_in_env():
    env = build_env(API_KEY, "openrouter", {})
    assert "OPENAI_API_BASE" not in env


def test_api_key_value_correct():
    key = "my-secret-key-xyz"
    env = build_env(key, "openai", {})
    assert env["OPENAI_API_KEY"] == key


def test_path_preserved():
    fake_path = "/usr/local/bin:/usr/bin:/bin"
    with patch.dict(os.environ, {"PATH": fake_path}):
        env = build_env(API_KEY, "openrouter", {})
    assert env["PATH"] == fake_path


def test_path_has_default_when_missing():
    env_without_path = {k: v for k, v in os.environ.items() if k != "PATH"}
    with patch.dict(os.environ, env_without_path, clear=True):
        env = build_env(API_KEY, "openrouter", {})
    assert "PATH" in env
    assert env["PATH"] != ""
