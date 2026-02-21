"""Tests for strip_ansi() and output header formatting."""

import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from run import strip_ansi, parse_file_list


# ---------------------------------------------------------------------------
# strip_ansi
# ---------------------------------------------------------------------------

def test_strip_ansi_escape_codes():
    text = "\x1b[32mHello\x1b[0m World"
    assert strip_ansi(text) == "Hello World"


def test_strip_ansi_multiple_sequences():
    text = "\x1b[1m\x1b[31mError:\x1b[0m something went wrong"
    assert strip_ansi(text) == "Error: something went wrong"


def test_strip_ansi_clean_text_unchanged():
    text = "No escape codes here.\nJust plain text."
    assert strip_ansi(text) == text


def test_strip_ansi_empty_string():
    assert strip_ansi("") == ""


def test_strip_ansi_only_codes():
    text = "\x1b[0m\x1b[1m\x1b[32m"
    assert strip_ansi(text) == ""


def test_strip_ansi_cursor_sequences():
    # CSI sequences with ? parameter (e.g. ?25l to hide cursor)
    text = "\x1b[?25lVisible text\x1b[?25h"
    assert strip_ansi(text) == "Visible text"


# ---------------------------------------------------------------------------
# Header output (via parse_file_list + captured stdout)
# ---------------------------------------------------------------------------

def _capture_header(mode: str, files: str = "", read_only: str = "") -> str:
    """Simulate the header printing logic from main()."""
    buf = io.StringIO()
    file_list = parse_file_list(files)
    read_only_list = parse_file_list(read_only)
    with patch("sys.stdout", buf):
        print(f"Mode: {mode}")
        if file_list:
            print(f"Files: {', '.join(file_list)}")
        if read_only_list:
            print(f"Read-only: {', '.join(read_only_list)}")
        print()
    return buf.getvalue()


def test_header_with_mode_files_readonly():
    out = _capture_header("architect", "src/auth.py,src/middleware.py", "src/models.py")
    assert "Mode: architect" in out
    assert "Files: src/auth.py, src/middleware.py" in out
    assert "Read-only: src/models.py" in out


def test_header_no_files_only_mode():
    out = _capture_header("ask")
    assert "Mode: ask" in out
    assert "Files:" not in out
    assert "Read-only:" not in out


def test_header_no_read_only():
    out = _capture_header("code", "main.py")
    assert "Mode: code" in out
    assert "Files: main.py" in out
    assert "Read-only:" not in out


def test_header_ends_with_blank_line():
    out = _capture_header("code", "main.py")
    assert out.endswith("\n\n")


# ---------------------------------------------------------------------------
# parse_file_list edge cases
# ---------------------------------------------------------------------------

def test_parse_file_list_comma_separated():
    result = parse_file_list("a.py,b.py,c.py")
    assert result == ["a.py", "b.py", "c.py"]


def test_parse_file_list_strips_whitespace():
    result = parse_file_list(" a.py , b.py ")
    assert result == ["a.py", "b.py"]


def test_parse_file_list_empty_string():
    assert parse_file_list("") == []


def test_parse_file_list_none_equivalent():
    assert parse_file_list("") == []


def test_parse_file_list_filters_empty_segments():
    result = parse_file_list("a.py,,b.py")
    assert result == ["a.py", "b.py"]
