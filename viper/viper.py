"""Viper is an application configuration system.
It believes that applications can be configured a variety of ways
via flags, ENVIRONMENT variables, configuration files retrieved
from the file system, or a remote key/value store.
Each item takes precedence over the item below it:

1. overrides
2. flags
3. env. variables
4. config file
5. key/value store
6. defaults
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Viper:
    """
    Viper is a prioritized configuration registry
    It maintains a set of configuration sources, fetches values to populate those,
    and provides them according to the source's priority.
    The priority of the sources is the following:
    1. overrides
    2. flags
    3. env. variables
    4. config file
    5. key/value store
    6. defaults

    For example, if values from the following sources were loaded:

        Defaults : {
            "secret": "",
            "user": "default",
            "endpoint": "https://localhost"
        }
        Config : {
            "user": "root"
            "secret": "defaultsecret"
        }
        Env : {
            "secret": "somesecretkey"
        }

    The resulting config will have the following values:
        {
            "secret": "somesecretkey",
            "user": "root",
            "endpoint": "https://localhost"
        }

    Note: Vipers are not safe for concurrent Get() and Set() operations"""

    def __init__(self):
        self._key_delim: str = "."
        self._config_paths: List[str] = []
        self._config_name: str = "config"
        self._config_file: Optional[str] = None
        self._config_type: Optional[str] = None
        self._config_permissions: int = 0o644
        self._env_prefix: Optional[str] = None
        self._env_key_replacer: Optional[StringReplacer] = None
        self._allow_empty_env: bool = False
        self._automatic_env_applied: bool = False
        self._config: Dict[str, Any] = {}


class StringReplacer(ABC):
    """applies a set of replacements to a string"""

    @abstractmethod
    def replace(self, s: str) -> str:
        """returns a copy of s with all replacements performed"""


class Error(ABC, Exception):
    def __init__(self, err: Exception):
        self.err = err

    @abstractmethod
    def __str__(self):
        pass


class ConfigMarshalError(Error):
    def __str__(self):
        return f"While marshaling config: {self.err}"
