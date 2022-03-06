"""
This module represents configuration class
"""

import json
import pathlib
import sys
from pathlib import Path

if sys.hexversion < 0x30A0000:
    raise Exception("Python version must be 3.10 or later")


class ConfigException(Exception):
    """
    Raise when we cannot parse arguments or open json file
    """


class Config:
    """
    It is a singleton class that stores application settings, defined in json file, as dictionary
    """

    _instance = None
    _properties = None
    _default_file_path = Path(__file__).resolve().parent / "default_config.json"
    graph_patterns = None
    analysis_patterns = None

    def __new__(cls, *args, **kwargs):
        if not Config._instance:
            Config._instance = super(Config, cls).__new__(cls)
        return Config._instance

    def __init__(self, file_path=None):
        self._file_path = file_path or Config._default_file_path
        self._json_data = self._load_from_json()
        Config.graph_patterns, Config.analysis_patterns = self._open_patterns_files()
        Config._properties = {}

        for name, value in self._json_data.items():
            Config._properties[name] = value

    @staticmethod
    def _open_patterns_files() -> tuple:
        path = pathlib.Path(__file__).parents[1] / "math" / "graph_patterns.json"
        path.resolve()
        try:
            with open(path, "r", encoding="utf-8") as file:
                graph_patterns = json.load(file)
        except IOError as err:
            raise ConfigException(f"Cannot open file '{path}'") from err

        path = pathlib.Path(__file__).parents[1] / "math" / "analyse_patterns.json"
        path.resolve()
        try:
            with open(path, "r", encoding="utf-8") as file:
                analysis_patterns = json.load(file)
        except IOError as err:
            raise ConfigException(f"Cannot open file '{path}'") from err

        return graph_patterns, analysis_patterns

    def _load_from_json(self) -> dict:
        try:
            with open(self._file_path, encoding="utf-8") as cfg_file:
                return json.load(cfg_file)
        except IOError as err:
            raise ConfigException(f"Cannot open file '{self._file_path}'") from err

    @property
    def properties(self) -> dict:
        """
        :return: config properties as a dictionary
        """
        return self._properties
