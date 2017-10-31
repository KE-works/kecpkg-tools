import click as click

from kecpkg.commands.utils import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Build the package and create a kecpkg file")
def build(**options):
    print('DO BUILD STUFF HERE ')