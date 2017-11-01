import click as click

from kecpkg.commands.utils import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Upload package to a KE-chain 2 scope")
def upload(**options):
    """Upload built kecpkg to KE-chain."""
    print('UPLOAD BUILDED KECPKG HERE ')
