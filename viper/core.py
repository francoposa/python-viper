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
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

import click

from viper.option import lookup_click_option, Option


class Viper:  # pylint: disable=too-many-instance-attributes
    """Viper is a in-process prioritized configuration registry

    Viper maintains a set of configuration sources and retrieves values
     from them according to the source's priority.
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
        self._override: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._kvstore: Dict[str, Any] = {}
        self._options: Dict[str, Option] = {}
        self._env: Dict[str, Any] = {}
        self._aliases: Dict[str, Any] = {}
        self._type_by_default_value: bool = False

    def config(self, config_func: Config):
        """applies callable option to Viper instance"""
        config_func(self)

    def get(self, key: str) -> Any:
        option: Optional[Option] = self._options.get(key)
        if not option:
            return None
        return option.value_string


ConfigFunc = Callable[[Viper], Any]


class Config:  # pylint: disable=too-few-public-methods
    """Config is a Callable used to apply configuration to a Viper instance via closures

    see https://commandcenter.blogspot.com/2014/01/self-referential-functions-and-design.html
    and https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis.

    The Config may access a "protected" member of the Viper instance
    in order to stay relatively consistent with the Go API, where
    attributes are private to a particular package, not a class
    """

    def __init__(self, config_func: ConfigFunc):
        self._config_func = config_func

    def __call__(self, viper: Viper):
        self._config_func(viper)


def key_delimiter(delimiter: str) -> Config:
    """sets the delimiter used for determining key parts"""

    def _key_delimiter(viper: Viper):
        viper._key_delim = delimiter  # pylint: disable=protected-access

    return Config(_key_delimiter)


class StringReplacer(ABC):  # pylint: disable=too-few-public-methods
    """StringReplacer applies a set of replacements to a string"""

    @abstractmethod
    def replace(self, string: str) -> str:  # pylint: disable=invalid-name
        """returns a copy of string with all replacements performed"""


def bind_option(viper: Viper, key: str, option: Option):
    # if not isinstance(option, Option):
    #     raise TypeError("option must implement Option interface")
    viper._options[key.lower()] = option
