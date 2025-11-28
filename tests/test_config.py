import os
import toml
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from aoc.config import _Config, find_config_file, CONFIG_FILENAME


# -------------------------------------------------------------------
# find_config_file()
# -------------------------------------------------------------------

def test_find_config_file_none_found(tmp_path):
    # temp dir has no .aoc.toml
    result = find_config_file(start=tmp_path)
    assert result is None


def test_find_config_file_in_current_dir(tmp_path):
    config_file = tmp_path / CONFIG_FILENAME
    config_file.write_text("year = 2023")
    result = find_config_file(start=tmp_path)
    assert result == config_file


def test_find_config_file_in_parent_dir(tmp_path):
    parent = tmp_path
    child = tmp_path / "sub"
    child.mkdir()

    cfg = parent / CONFIG_FILENAME
    cfg.write_text("day = 5")

    result = find_config_file(start=child)
    assert result == cfg


# -------------------------------------------------------------------
# _Config: loading existing config
# -------------------------------------------------------------------

@patch("aoc.config.find_config_file")
def test_config_loads_existing_file(mock_find, tmp_path):
    cfg = tmp_path / CONFIG_FILENAME
    cfg.write_text("year = 2023\nday = 7\ncookie = 'XYZ'")

    mock_find.return_value = cfg
    c = _Config()

    assert c.year == 2023
    assert c.day == 7
    assert c.cookie == "XYZ"


@patch("aoc.config.find_config_file")
def test_config_load_invalid_file_gracefully(mock_find, tmp_path):
    cfg = tmp_path / CONFIG_FILENAME
    cfg.write_text("{not:toml:at:all!")

    mock_find.return_value = cfg
    c = _Config()

    # Invalid TOML should result in empty config
    assert c.list() == {}


# -------------------------------------------------------------------
# Getters / Setters / Deleters
# -------------------------------------------------------------------

@patch("aoc.config.find_config_file", return_value=None)
def test_config_set_year_creates_file(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()

    c.year = 2024

    saved = toml.load(tmp_path / CONFIG_FILENAME)
    assert saved["year"] == 2024
    assert c.year == 2024


@patch("aoc.config.find_config_file", return_value=None)
def test_config_set_day_creates_file(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()

    c.day = 9

    saved = toml.load(tmp_path / CONFIG_FILENAME)
    assert saved["day"] == 9
    assert c.day == 9


@patch("aoc.config.find_config_file", return_value=None)
def test_config_set_cookie_creates_file(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()

    c.cookie = "ABCDEF"

    saved = toml.load(tmp_path / CONFIG_FILENAME)
    assert saved["cookie"] == "ABCDEF"
    assert c.cookie == "ABCDEF"


@patch("aoc.config.find_config_file", return_value=None)
def test_config_delete_year(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()

    c.year = 2023
    del c.year

    saved = toml.load(tmp_path / CONFIG_FILENAME)
    assert "year" not in saved
    assert c.year is None


@patch("aoc.config.find_config_file", return_value=None)
def test_config_delete_all_date(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()
    c.year = 2023
    c.day = 5

    del c.date  # deletes both year/day

    saved = toml.load(tmp_path / CONFIG_FILENAME)
    assert "year" not in saved
    assert "day" not in saved
    assert c.year is None
    assert c.day is None


# -------------------------------------------------------------------
# date getter / setter
# -------------------------------------------------------------------

@patch("aoc.config.find_config_file", return_value=None)
def test_config_date_getter(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()
    c.year = 2023
    c.day = 4
    assert c.date == (2023, 4)


@patch("aoc.config.find_config_file", return_value=None)
def test_config_date_setter_valid(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()

    c.date = (2022, 8)

    saved = toml.load(tmp_path / CONFIG_FILENAME)
    assert saved["year"] == 2022
    assert saved["day"] == 8
    assert c.date == (2022, 8)


@patch("aoc.config.find_config_file", return_value=None)
def test_config_date_setter_invalid_type(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()

    with pytest.raises(ValueError):
        c.date = "2023-5"


@patch("aoc.config.find_config_file", return_value=None)
def test_config_date_setter_missing_day(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()

    with pytest.raises(ValueError):
        c.date = (2023, None)


# -------------------------------------------------------------------
# clear()
# -------------------------------------------------------------------

@patch("aoc.config.find_config_file", return_value=None)
def test_config_clear(_mock_find, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = _Config()
    c.year = 2022
    c.day = 1
    c.cookie = "XYZ"

    c.clear()

    saved = toml.load(tmp_path / CONFIG_FILENAME)
    assert saved == {}
    assert c.list() == {}
