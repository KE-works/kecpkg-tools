import os

import click

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.utils import remove_path, get_package_dir, echo_success, echo_failure, echo_warning


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Purge and delete a project (No reverse)")
@click.argument('package', required=False)
@click.option('--force', '-f', is_flag=True, help="Force purge (no confirmation)")
def purge(package, **options):
    """
    Purge and clean a package directory structure.

    :param package: Name of the kecpkg package
    :param options:
    :return:
    """
    package_name = package or click.prompt('Provide package name')
    package_dir = get_package_dir(package_name)

    if os.path.exists(package_dir):
        if options.get('force') or click.confirm(
                "Do you want to purge and completely remove '{}'?".format(package_name)):
            remove_path(package_dir)
            if not os.path.exists(package_dir):
                echo_success('Package `{}` is purged and removed from disk'.format(package_name))
            else:
                echo_failure('Something went wrong pruning pacakage `{}`'.format(package_name))
        else:
            echo_warning('Package `{}` will not be purged'.format(package_name))
    else:
        echo_failure('Package `{}` does not exist'.format(package_name))
