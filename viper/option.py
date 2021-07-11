from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

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


def lookup_click_option(command: click.Command, name: str) -> ClickOption:
    click_params: List[click.Parameter] = command.params
    try:
        # here we assume click internals force unique parameter names and
        # that the click.Option we are attempting to bind to has a name.
        # In rare cases click.Option instances may have name=None but
        # if you're trying to bind to the Option, we assume it has a name
        click_param: click.Parameter = next(
            filter(lambda x: x.name == name, click_params)
        )
    except StopIteration as e:
        raise ClickOptionNotFoundError(name, click_ctx) from e

    _is_click_option(click_param, raise_err=True)
    return ClickOption(
        name=name,
        option=click_param,  # type: ignore  # this Parameter is an Option
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

    def source(self) -> Source:
        ctx: click.Context = click.get_current_context()
        click_source = ctx.get_parameter_source(self.option.name)


class ClickOptionInvalidError(TypeError):
    def __str__(self):
        return "option must be of type click.Option"


class ClickOptionNotFoundError(Exception):
    def __init__(self, name: str, command: click.Command):
        self.option_name = name
        self.command = command

    def __str__(self):
        return (
            f"option with name {self.option_name} not found in current"
            f"click command context '{self.command.name}'"
        )
