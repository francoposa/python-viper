import click
from click.testing import Result

from viper.core import bind_option, Viper
from viper.option import lookup_click_option, Option

viper = Viper()


@click.command()
@click.argument("argument")
@click.option("--option", default=0, help="an integer option")
def cmd(argument, option):
    click.echo(argument)
    viper_option: str = viper.get("option")
    click.echo(viper_option)
    click.echo(option)


def test_cmd(cli_runner):
    click_option: Option = lookup_click_option(cmd, "option")
    bind_option(viper, "option", click_option)
    result: Result = cli_runner.invoke(cmd, args=["argument", "--option", "1"])
    assert result.output.splitlines() == ["argument", "1", "1"]
