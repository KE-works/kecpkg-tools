import click

from kecpkg_tools.cli import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help='Creates a new Python project')
@click.argument('name', required=False)
def new(name, **kwargs):
    print(kwargs)
