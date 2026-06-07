import sys
import io
import platform
import pytest
from bin.clean_ids import main, is_valid_youtube_id


def test_valid_id_passes(monkeypatch, capsys):
    fake_input = io.StringIO("kcFsuxaJ1es\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == "kcFsuxaJ1es\n"

def test_invalid_id_filtered(monkeypatch, capsys):
    fake_input = io.StringIO("asd123\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""

def test_valid_then_invalid_then_valid(monkeypatch, capsys):
    fake_input = io.StringIO("kcFsuxaJ1es\nasd123\nDQw4w9WgXcQ\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == "kcFsuxaJ1es\nDQw4w9WgXcQ\n"

def test_only_bad_lines(monkeypatch, capsys):
    fake_input = io.StringIO("bad\n!!!\ntooshort\n")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""

def test_empty_input(monkeypatch, capsys):
    fake_input = io.StringIO("")
    monkeypatch.setattr(sys, "stdin", fake_input)
    main()
    captured = capsys.readouterr()
    assert captured.out == ""

def test_exactly_11_chars_valid():
    assert is_valid_youtube_id("kcFsuxaJ1es") is True

def test_10_chars_invalid():
    assert is_valid_youtube_id("kcFsuxaJ1e") is False

def test_12_chars_invalid():
    assert is_valid_youtube_id("kcFsuxaJ1esX") is False

def test_special_chars_invalid():
    assert is_valid_youtube_id("kcFsux!J1e@") is False

def test_underscore_and_dash_valid():
    assert is_valid_youtube_id("abc_def-123") is True

def test_running_on_ubuntu():
    assert platform.system() == "Linux"
    with open("/etc/os-release") as f:
        content = f.read().lower()
    assert "ubuntu" in content

def test_python_version():
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 8

@pytest.mark.xfail(reason="12-char ID should not pass")
def test_expected_to_fail():
    assert is_valid_youtube_id("kcFsuxaJ1esX") is True

@pytest.mark.skip(reason="Feature not yet implemented")
def test_whitespace_only_line():
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
    assert is_valid_youtube_id(youtube_id) == expected
