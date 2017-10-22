import click

from kecpkg_tools.commands.new import new

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}
UNKNOWN_OPTIONS = {
    'ignore_unknown_options': True,
    **CONTEXT_SETTINGS
}


class AliasedGroup(click.Group):  # no cov
    def get_command(self, ctx, cmd_name):
        return click.Group.get_command(self, ctx, cmd_name)


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option()
def kecpkg():
    pass


kecpkg.add_command(new)
