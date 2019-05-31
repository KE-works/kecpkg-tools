import click

from kecpkg.commands.build import build
from kecpkg.commands.new import new
from kecpkg.commands.prune import prune
from kecpkg.commands.purge import purge
from kecpkg.commands.sign import sign
from kecpkg.commands.upload import upload
from kecpkg.commands.config import config
from kecpkg.commands.utils import CONTEXT_SETTINGS


class AliasedGroup(click.Group):
    """Intermediate class to combine the kecpkg command groups."""

    pass


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option()
def kecpkg():
    """KE-chain Package manager toolset."""
    pass


kecpkg.add_command(new)
kecpkg.add_command(build)
kecpkg.add_command(upload)
kecpkg.add_command(purge)
kecpkg.add_command(prune)
kecpkg.add_command(config)
kecpkg.add_command(sign)
