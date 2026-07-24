"""Tests for the clean_ids pipeline module."""
import sys
import io
import platform
import pytest
from bin.clean_ids import main, is_valid_youtube_id


def test_valid_id_passes(monkeypatch, capsys):
    """Verifies a valid 11-char ID passes through to stdout."""
    fake_input = io.StringIO("kcFsuxaJ1es\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == "kcFsuxaJ1es\n"


def test_invalid_id_filtered(monkeypatch, capsys):
    """Verifies a short invalid ID is filtered from stdout."""
    fake_input = io.StringIO("asd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_valid_then_invalid_then_valid(monkeypatch, capsys):
    """Verifies only valid IDs pass when mixed with invalid ones."""
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\nDQw4w9WgXcQ\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == "kcFsuxaJ1es\nDQw4w9WgXcQ\n"


def test_only_bad_lines(monkeypatch, capsys):
    """Verifies all bad lines produce empty stdout."""
    fake_input = io.StringIO("bad\n!!!\ntooshort\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_empty_input(monkeypatch, capsys):
    """Verifies empty stdin produces empty stdout."""
    fake_input = io.StringIO("")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_exactly_11_chars_valid():
    """Verifies exactly 11 alphanumeric chars is valid."""
    assert is_valid_youtube_id("kcFsuxaJ1es") is True


def test_10_chars_invalid():
    """Verifies 10-char ID is invalid."""
    assert is_valid_youtube_id("kcFsuxaJ1e") is False


def test_12_chars_invalid():
    """Verifies 12-char ID is invalid."""
    assert is_valid_youtube_id("kcFsuxaJ1esX") is False


def test_special_chars_invalid():
    """Verifies IDs with special characters are invalid."""
    assert is_valid_youtube_id("kcFsux!J1e@") is False


def test_underscore_and_dash_valid():
    """Verifies underscores and dashes are allowed."""
    assert is_valid_youtube_id("abc_def-123") is True


def test_running_on_ubuntu():
    """Verifies the test environment is running on Ubuntu Linux."""
    assert platform.system() == "Linux"
    with open("/etc/os-release", encoding="utf-8") as f:
        content = f.read().lower()
    assert "ubuntu" in content


def test_python_version():
    """Verifies Python version is 3.8 or higher."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 8


@pytest.mark.xfail(reason="12-char ID should not pass")
def test_expected_to_fail():
    """Expected failure: 12-char ID should not be valid."""
    assert is_valid_youtube_id("kcFsuxaJ1esX") is True


@pytest.mark.skip(reason="Feature not yet implemented")
def test_whitespace_only_line():
    """Skipped: whitespace-only line handling not yet implemented."""
    assert is_valid_youtube_id("           ") is False


@pytest.mark.parametrize("youtube_id,expected", [
    ("kcFsuxaJ1es", True),
    ("DQw4w9WgXcQ", True),
    ("abc_def-123", True),
    ("tooshort",    False),
    ("toolongidXXX", False),
    ("invalid!@#$%", False),
    ("",            False),
])
def test_parametrized_ids(youtube_id, expected):
    """Verifies is_valid_youtube_id against a range of valid and invalid IDs."""
    assert is_valid_youtube_id(youtube_id) == expected
