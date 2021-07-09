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

from viper.core.flag import ClickFlag, Flag


class Viper:  # pylint: disable=too-many-instance-attributes
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
        self._override: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._kvstore: Dict[str, Any] = {}
        self._flags: Dict[str, Flag] = {}
        self._env: Dict[str, Any] = {}
        self._aliases: Dict[str, Any] = {}
        self._type_by_default_value: bool = False

    def option(self, option_func: Option):
        """applies callable option to Viper instance"""
        option_func(self)


class Option:  # pylint: disable=too-few-public-methods
    """Callable class used to apply option settings to a Viper instance via closures

    see https://commandcenter.blogspot.com/2014/01/self-referential-functions-and-design.html
    and https://dave.cheney.net/2014/10/17/functional-options-for-friendly-apis.
    """

    def __init__(self, option_func: Callable[[Viper], Any]):
        self._option_func = option_func

    def __call__(self, viper: Viper):
        # the Option may access a protected member of the Viper instance
        # in order to stay consistent with the Go API, where
        # attributes are private to a particular package, not a class
        self._option_func(viper)


def key_delimiter(delimiter: str) -> Option:
    """sets the delimiter used for determining key parts"""

    def _key_delimiter(viper: Viper):
        viper._key_delim = delimiter  # pylint: disable=protected-access

    return Option(_key_delimiter)


class StringReplacer(ABC):  # pylint: disable=too-few-public-methods
    """applies a set of replacements to a string"""

    @abstractmethod
    def replace(self, string: str) -> str:  # pylint: disable=invalid-name
        """returns a copy of string with all replacements performed"""


def bind_click_flag(viper: Viper, key: str, flag: ClickFlag):
    pass
