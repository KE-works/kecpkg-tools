import click

from kecpkg.commands.build import build
from kecpkg.commands.new import new
from kecpkg.commands.upload import upload

from kecpkg.commands.utils import CONTEXT_SETTINGS


class AliasedGroup(click.Group):
    pass


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option()
def kecpkg():
    pass


kecpkg.add_command(new)
kecpkg.add_command(build)
kecpkg.add_command(upload)
