from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

import click

from viper.source import Source


class Option(ABC):
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


def lookup_click_option(command: click.Command, key: str) -> ClickOption:
    click_params: List[click.Parameter] = command.params
    # here we assume click internals force unique parameter names and
    # that the click.Option we are attempting to bind to has a name.
    # In rare cases click.Option instances may have name=None but
    # if you're trying to bind to the Option, we assume it has a name
    matching_param: Optional[click.Parameter] = None
    for click_param in click_params:
        if click_param.name == key:
            matching_param = click_param
            break

    if not matching_param:
        raise ClickOptionNotFoundError(command, key)

    _is_click_option(matching_param, raise_err=True)
    return ClickOption(
        name=key,
        option=matching_param,  # type: ignore  # this Parameter is an Option
    )


def _is_click_option(flag: click.Parameter, raise_err=False) -> bool:
    is_valid = isinstance(flag, click.Option)
    if not is_valid and raise_err:
        raise ClickOptionInvalidError()
    return is_valid


class ClickOption:
    def __init__(self, name: str, option: click.Option):
        self.name = name
        _is_click_option(option, raise_err=True)
        self.option = option

    @property
    def source(self) -> Source:
        ctx: click.Context = click.get_current_context()
        click_source = ctx.get_parameter_source(self.option.name)

    @property
    def value_string(self) -> str:
        ctx: click.Context = click.get_current_context()
        return str(ctx.params[self.name])


class ClickOptionInvalidError(TypeError):
    def __str__(self):
        return "option must be of type click.Option"


class ClickOptionNotFoundError(Exception):
    def __init__(
        self, command: click.Command, key: str
    ):  # pylint: disable=super-init-not-called
        self.command = command
        self.key = key

    def __str__(self):
        return (
            f"option with name {self.key} not found in "
            f"click command '{self.command}'"
        )
