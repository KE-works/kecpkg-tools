import click
import os

import sys

from kecpkg.commands.utils import echo_warning, echo_failure, echo_success, CONTEXT_SETTINGS
from kecpkg.settings import load_settings, copy_default_settings


@click.command(short_help="Create a new kecpkg SIM script project",
               context_settings=CONTEXT_SETTINGS)
@click.argument('name', required=False)
def new(name=None, **options):
    """
    Created new package directory structure

    :param name: Name of the kecpkg project
    :param options:
    :return:
    """
    print('___ DO NEW STUFF HERE ')

    try:
        settings = load_settings()
    except FileNotFoundError:
        settings = copy_default_settings()
        echo_warning(
            'The default project structure will be used.'
        )
    pkg_root = os.getcwd()
    package_name = name or click.prompt("Project name")

    pkg_dir = os.path.join(pkg_root, package_name)
    if os.path.exists(pkg_dir):
        echo_failure("Directory '{}' already exists.".format(pkg_dir))
        sys.exit(1)

    if not name:
        settings['version'] = click.prompt('Version', default='0.0.1')
        settings['description'] = click.prompt('Description', default='')
        settings['name'] = click.prompt('Author', default=settings.get('name', ''))
        settings['email'] = click.prompt('Author\'s email', default=settings.get('email', ''))
        settings['python_version'] = click.prompt('Python version (choose from: {})'.format(settings.get('pyversions')), default='3.5')


    # feed back stuff here.
    echo_success(settings)
