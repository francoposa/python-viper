from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Type

import click

from viper.core.error import ViperError
from viper.core.source import Source


class Flag(ABC):
    @property
    @abstractmethod
    def source(self) -> Source:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def value_string(self) -> str:
        pass

    @property
    @abstractmethod
    def value_type(self) -> str:
        pass


def lookup_click_flag(name: str) -> ClickFlag:
    click_ctx = click.get_current_context()
    click_params: List[click.Parameter] = click_ctx.command.params
    try:
        click_param: click.Parameter = next(
            filter(lambda x: x.name == name, click_params)
        )
    except StopIteration as e:
        raise ClickFlagNotFoundError(name, click_ctx) from e

    _is_valid_click_flag(click_param, raise_err=True)
    return ClickFlag(name=name, flag=click_param)  # type: ignore


def _is_valid_click_flag(flag: click.Parameter, raise_err=False) -> bool:
    is_valid = isinstance(flag, click.Option) and flag.is_flag
    if not is_valid and raise_err:
        raise ClickFlagInvalidError()
    return is_valid


class ClickFlag:
    def __init__(self, name: str, flag: click.Option):
        self.name = name
        _is_valid_click_flag(flag, raise_err=True)
        self.flag = flag

    def source(self) -> Source:
        ctx = click.get_current_context()
        click_source = ctx.get_parameter_source(self.flag.name)


class ClickFlagInvalidError(TypeError, ValueError):
    def __str__(self):
        return "flag must be of type click.Option with is_flag=True"


class ClickFlagNotFoundError(Exception):
    def __init__(self, name: str, click_ctx: click.Context):
        self.flag_name = name
        self.click_ctx = click_ctx

    def __str__(self):
        return (
            f"flag with name {self.flag_name} not found in current"
            f"click command context '{self.click_ctx.command.name}'"
        )
