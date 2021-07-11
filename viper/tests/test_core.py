import click

from viper.core import Viper
from viper.option import lookup_click_option


@click.command()
@click.option("--option", default=1, help="an integer option")
@click.argument("argument")
def cmd(option, argument):
    click.echo(f"option: {option}")
    click.echo(f"argument: {argument}")


viper = Viper()


def main():
    lookup_click_option(cmd, "option")
    cmd()


if __name__ == "__main__":
    main()  # pylint disable=no-value-for-parameter
