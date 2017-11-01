import os
import sys

import click

from kecpkg.commands.utils import echo_failure, CONTEXT_SETTINGS, echo_info, echo_success
from kecpkg.create import create_package, create_venv
from kecpkg.settings import load_settings, copy_default_settings, save_settings
from kecpkg.utils import normalise_name


@click.command(short_help="Create a new kecpkg SIM script package",
               context_settings=CONTEXT_SETTINGS)
@click.argument('name', required=False)
@click.option('--venv', help="name of the virtual python environment to create")
@click.option('--script', help="name of the script inside the package that contains the entrypoint")
@click.option('--global-packages', is_flag=True,
              help='Gives created virtual envs access to the global site-packages.')
@click.option('--no-venv', help="suppress the creation of the virtual environment", is_flag=True)
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def new(name=None, **options):
    """
    Created new package directory structure

    :param name: Name of the kecpkg package
    :param options:
    :return:
    """
    try:
        settings = load_settings()
    except FileNotFoundError:
        settings = copy_default_settings()
    package_root_dir = os.getcwd()

    # set the package name, clean an normalise using snake_case
    package_name = name or click.prompt("Project name")
    package_name = normalise_name(package_name)

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
        settings['python_version'] = click.prompt('Python version (choose from: {})'.format(settings.get('pyversions')),
                                                  default='3.5')
    if options.get('script'):
        script_base = normalise_name(options.get('script').replace('.py', ''))
        echo_info('Setting the script to `{}`'.format(script_base))
        settings['entrypoint_script'] = script_base

    if options.get('venv'):
        settings['venv_dir'] = normalise_name(options.get('venv'))

    echo_info("Creating package structure")
    create_package(package_dir, settings=settings)
    if not options.get('no_venv'):
        echo_info("Creating virtual environment")
        create_venv(package_dir, settings, pypath=None, use_global=options.get('global_packages'),
                    verbose=options.get('verbose'))
    else:
        settings['venv_dir'] = None

    # save the settings (in the package_dir)
    save_settings(settings, package_dir=package_dir)

    echo_success('Package `{package_name}` created in `{package_dir}`'.format(package_name=package_name,
                                                                              package_dir=package_dir))
