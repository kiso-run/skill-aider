"""Tests for build_command()."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from run import build_command, parse_file_list


AIDER_BIN = str(Path(sys.executable).parent / "aider")


def test_default_config_architect_flags(full_config):
    cmd = build_command({"message": "do something"}, full_config, "architect")
    assert "--architect" in cmd
    assert "--ask" not in cmd


def test_mode_code_no_extra_flag(full_config):
    cmd = build_command({"message": "do something"}, full_config, "code")
    assert "--architect" not in cmd
    assert "--ask" not in cmd


def test_mode_ask_flag(full_config):
    cmd = build_command({"message": "explain auth"}, full_config, "ask")
    assert "--ask" in cmd
    assert "--architect" not in cmd


def test_mode_override_args_over_config(full_config):
    # Even if config says "architect", if caller passes "ask" it should use ask
    cmd = build_command({"message": "explain", "mode": "ask"}, full_config, "ask")
    assert "--ask" in cmd


def test_models_in_command(full_config):
    cmd = build_command({"message": "x"}, full_config, "architect")
    assert "--model" in cmd
    idx = cmd.index("--model")
    assert cmd[idx + 1] == full_config["architect_model"]

    assert "--editor-model" in cmd
    idx = cmd.index("--editor-model")
    assert cmd[idx + 1] == full_config["editor_model"]

    assert "--weak-model" in cmd
    idx = cmd.index("--weak-model")
    assert cmd[idx + 1] == full_config["weak_model"]


def test_map_tokens_in_command(full_config):
    cmd = build_command({"message": "x"}, full_config, "architect")
    assert "--map-tokens" in cmd
    idx = cmd.index("--map-tokens")
    assert cmd[idx + 1] == str(full_config["map_tokens"])


def test_editor_edit_format_in_command(full_config):
    cmd = build_command({"message": "x"}, full_config, "architect")
    assert "--editor-edit-format" in cmd
    idx = cmd.index("--editor-edit-format")
    assert cmd[idx + 1] == full_config["editor_edit_format"]


def test_commit_language_in_command(full_config):
    cmd = build_command({"message": "x"}, full_config, "architect")
    assert "--commit-language" in cmd
    idx = cmd.index("--commit-language")
    assert cmd[idx + 1] == full_config["commit_language"]


def test_auto_commits_true(full_config):
    full_config["auto_commits"] = True
    cmd = build_command({"message": "x"}, full_config, "code")
    assert "--auto-commits" in cmd
    assert "--no-auto-commits" not in cmd


def test_auto_commits_false():
    config = {"auto_commits": False}
    cmd = build_command({"message": "x"}, config, "code")
    assert "--no-auto-commits" in cmd
    assert "--auto-commits" not in cmd


def test_files_as_positional_args(full_config):
    cmd = build_command(
        {"message": "x", "files": "src/auth.py,src/middleware.py"},
        full_config,
        "code",
    )
    assert "src/auth.py" in cmd
    assert "src/middleware.py" in cmd


def test_read_only_files_as_read_flags(full_config):
    cmd = build_command(
        {"message": "x", "read_only_files": "src/models.py,src/schema.py"},
        full_config,
        "architect",
    )
    read_flags = [cmd[i + 1] for i, v in enumerate(cmd) if v == "--read"]
    assert "src/models.py" in read_flags
    assert "src/schema.py" in read_flags


def test_custom_api_base_flag():
    config = {"api_base": "https://proxy.example.com/v1"}
    cmd = build_command({"message": "x"}, config, "code")
    assert "--openai-api-base" in cmd
    idx = cmd.index("--openai-api-base")
    assert cmd[idx + 1] == "https://proxy.example.com/v1"


def test_non_interactive_flags_always_present(full_config):
    cmd = build_command({"message": "x"}, full_config, "architect")
    assert "--yes" in cmd
    assert "--no-pretty" in cmd
    assert "--no-fancy-input" in cmd
    assert "--no-suggest-shell-commands" in cmd


def test_empty_files_no_extra_args(full_config):
    cmd = build_command({"message": "x", "files": ""}, full_config, "code")
    # Positional file args should not appear
    # (can't check by name, but --read should also be absent)
    assert "--read" not in cmd


def test_missing_optional_args_handled(no_config):
    # Should not raise even with empty config and minimal args
    cmd = build_command({"message": "hello"}, no_config, "code")
    assert "--message" in cmd
    assert cmd[cmd.index("--message") + 1] == "hello"


def test_aider_bin_resolved_from_executable():
    cmd = build_command({"message": "x"}, {}, "code")
    assert cmd[0] == AIDER_BIN


def test_message_always_present(full_config):
    cmd = build_command({"message": "fix the bug"}, full_config, "code")
    assert "--message" in cmd
    assert cmd[cmd.index("--message") + 1] == "fix the bug"
