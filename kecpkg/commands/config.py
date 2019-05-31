import os

import click
from tabulate import tabulate

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.settings import load_settings, copy_default_settings, save_settings, SETTINGS_FILENAME
from kecpkg.utils import get_package_dir, copy_path, echo_success, echo_info


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Finds and updated the configuration of the kecpkg")
@click.argument('package', required=False)
@click.option('--settings', '--config', '-s', 'settings_filename',
              help="path to the setting file (default `{}`".format(SETTINGS_FILENAME),
              type=click.Path(exists=True), default=SETTINGS_FILENAME)
@click.option('--init', is_flag=True, help="will init a settingsfile if not found")
@click.option('--interactive', '-i', is_flag=True, help="interactive mode; guide me through the settings")
@click.option('--get', '-g', 'get_key', help="Key to get and display", required=False)
@click.option('--set', '-s', 'set_key', nargs=2, help="Key to set <key> <value>. Value is set as string.",
              required=False)
@click.option('--verbose', '-v', is_flag=True, help="be more verbose (print settings)")
def config(package, **options):
    """Manage the configuration (or settings) of the package.

    The various settings in the .kecpkg-settings.json file are:

    package_name:   name of the package
    version:        version number of the package
    description:    longer description of the package
    name:           name of the author of the package
    email:          email of the author of the package
    python_version: python version on which the kecpkg will run, corresponds
                    with an executable KE-crunch environment
    entrypoint_script: the name of the script that will be executed first
    entrypoint_func: function name inside the script that will be executed.
                    Ensure that it takes *args, **kwargs.
    venv_dir:       python virtual environment directory in the development environment
    requirements_filename: name of the requirements file with list of package that
                    will be installed before running
    build_dir:      directory where the built kecpkg will be stored
    exclude_paths:  list of paths that will be excluded from the package, next to
                    the build in excludes
    url:            url where the package will be uploaded
    token:          token of the user under which the package is uploaded
    scope_id:       identification of the scope under which the package is uploaded
    service_id:     identification under which the package is re-uploaded
                    (or recently uploaded)
    last_upload:    date and time of the last upload
    """
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))

    if options.get('init'):
        if os.path.exists(os.path.join(package_dir, options.get('settings_filename'))) and \
                click.confirm('Are you sure you want to overwrite the current settingsfile '
                              '(old settings will be a backup)?'):
            copy_path(os.path.join(package_dir, options.get('settings_filename')),
                      os.path.join(package_dir, "{}-backup".format(options.get('settings_filename'))))
        echo_info('Creating new settingsfile')
        settings = copy_default_settings()
        settings['package_name'] = package_name
        save_settings(settings, package_dir=package_dir, settings_filename=options.get('settings_filename'))

    settings = load_settings(package_dir=package_dir)
    if options.get('interactive'):
        settings['version'] = click.prompt('Version', default=settings.get('version', '0.0.1'))
        settings['description'] = click.prompt('Description', default=settings.get('description', ''))
        settings['name'] = click.prompt('Author', default=settings.get('name', os.environ.get('USER', '')))
        settings['email'] = click.prompt('Author\'s email', default=settings.get('email', ''))
        settings['python_version'] = click.prompt('Python version (choose from: {})'.
                                                  format(settings.get('pyversions')), default='3.5')
        settings['exclude_paths'] = click.prompt("Exclude additional paths from kecpkg (eg. 'data, input')",
                                                 default=settings.get('exclude_paths', ''),
                                                 value_proc=process_additional_exclude_paths)
        save_settings(settings, package_dir=package_dir, settings_filename=options.get('settings_filename'))

    if options.get('set_key'):
        k, v = options.get('set_key')
        if options.get('verbose'):
            echo_info("Set the key '{}' to value '{}'".format(k, v))
        settings[k] = v
        save_settings(settings, package_dir=package_dir, settings_filename=options.get('settings_filename'))

    if options.get('get_key'):
        echo_info(tabulate([(options.get('get_key'), settings.get(options.get('get_key')))],
                           headers=("key", "value")))
        return

    if options.get('verbose'):
        echo_info(tabulate(settings.items(), headers=("key", "value")))

    if not options.get('interactive'):
        echo_success('Settings file identified and correct')


def process_additional_exclude_paths(raw_value):
    """Process additional list of exclude paths and return a list."""
    assert isinstance(raw_value, str), "The value should be a string, got: {}".format(type(raw_value))

    pathlist = []
    raw_pathlist = raw_value.split(',')
    for raw_path in raw_pathlist:
        pathlist.append(raw_path.strip())
    return pathlist
