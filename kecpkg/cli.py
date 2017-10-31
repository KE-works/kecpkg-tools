import click

from kecpkg.commands.build import build
from kecpkg.commands.new import new
from kecpkg.commands.prune import prune
from kecpkg.commands.purge import purge
from kecpkg.commands.upload import upload

from kecpkg.commands.utils import CONTEXT_SETTINGS, echo_info


class AliasedGroup(click.Group):
    pass


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option()
def kecpkg():
    pass


kecpkg.add_command(new)
kecpkg.add_command(build)
kecpkg.add_command(upload)
kecpkg.add_command(purge)
kecpkg.add_command(prune)
