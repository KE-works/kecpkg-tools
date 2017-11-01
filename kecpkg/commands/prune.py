import click

from kecpkg.commands.utils import CONTEXT_SETTINGS


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Removes a project's build artifacts")
@click.argument('package', required=False)
def prune(package, **options):
    print('DO PRUNE OF BUILD ARTIFACTS')
