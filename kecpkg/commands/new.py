import click
import os

import sys

from kecpkg.commands.utils import echo_warning, echo_failure, echo_success, CONTEXT_SETTINGS
from kecpkg.create import create_package, create_venv
from kecpkg.utils import snake_case
from kecpkg.settings import load_settings, copy_default_settings, save_settings


@click.command(short_help="Create a new kecpkg SIM script package",
               context_settings=CONTEXT_SETTINGS)
@click.argument('name', required=False)
@click.option('--venv', help="name of the virtual python environment to create")
def new(name=None, **options):
    """
    Created new package directory structure

    :param name: Name of the kecpkg package
    :param options:
    :return:
    """
    print('___ DO NEW STUFF HERE ')

    try:
        settings = load_settings()
    except FileNotFoundError:
        settings = copy_default_settings()
        echo_warning(
            'The default package structure will be used.'
        )
    package_root_dir = os.getcwd()
    package_name = name or click.prompt("Project name")
    package_name = snake_case(package_name)

    # save to settings
    settings['package_name'] = package_name

    package_dir = os.path.join(package_root_dir, package_name)
    if os.path.exists(package_dir):
        echo_failure("Directory '{}' already exists.".format(package_dir))
        sys.exit(1)

    if not name:
        settings['version'] = click.prompt('Version', default=settings.get('version', '0.0.1'))
        settings['description'] = click.prompt('Description', default='')
        settings['name'] = click.prompt('Author', default=settings.get('name', ''))
        settings['email'] = click.prompt('Author\'s email', default=settings.get('email', ''))
        settings['python_version'] = click.prompt('Python version (choose from: {})'.format(settings.get('pyversions')), default='3.5')

    if options.get('venv'):
        settings['venv_dir'] = snake_case(options.get('venv'))

    create_package(package_dir, package_name=package_name, settings=settings)
    print(create_venv(package_dir, settings, pypath=None, use_global=False, verbose=True))

    # feed back stuff here.
    print(settings)
    save_settings(settings, package_dir=package_dir)