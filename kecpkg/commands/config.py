import os

import click

from kecpkg.commands.utils import CONTEXT_SETTINGS, echo_info, echo_success
from kecpkg.settings import load_settings, copy_default_settings, save_settings, SETTINGS_FILENAME
from kecpkg.utils import get_package_dir, copy_path


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Finds and updated the configuration of the kecpkg")
@click.argument('package', required=False)
@click.option('--init', is_flag=True, help="will init a settingsfile if not found")
@click.option('--interactive', '-i', is_flag=True, help="interactive mode; guide me through the settings")
@click.option('--verbose', '-v', is_flag=True, help="be more verbose (print settings)")
def config(package, **options):
    """Manage the configuration (or settings) of the package."""
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))

    if options.get('init'):
        if os.path.exists(os.path.join(package_dir, SETTINGS_FILENAME)) and \
            click.confirm('Are you sure you want to overwrite the current settingsfile (old settings will be a backup)?'):
            copy_path(os.path.join(package_dir,SETTINGS_FILENAME),
                      os.path.join(package_dir, "{}-backup".format(SETTINGS_FILENAME)))
        echo_info('Creating new settingsfile')
        settings = copy_default_settings()
        settings['package_name'] = package_name
        save_settings(settings, package_dir=package_dir)

    settings = load_settings(package_dir=package_dir)
    if options.get('interactive'):
        settings['version'] = click.prompt('Version', default=settings.get('version', '0.0.1'))
        settings['description'] = click.prompt('Description', default=settings.get('description', ''))
        settings['name'] = click.prompt('Author', default=settings.get('name', os.environ.get('USER', '')))
        settings['email'] = click.prompt('Author\'s email', default=settings.get('email', ''))
        settings['python_version'] = click.prompt('Python version (choose from: {})'.format(settings.get('pyversions')),
                                                  default='3.5')
        save_settings(settings, package_dir=package_dir)

    if options.get('verbose'):
        for k, v in settings.items():
            echo_info("  {}: '{}'".format(k, v))

    if not options.get('interactive'):
        echo_success('Settings file identified and correct')
