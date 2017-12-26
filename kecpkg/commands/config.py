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
    """Manage the configuration (or settings) of the package.

    The various settings in the .kecpkg-settings.json file are:

    \b
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
    last_upload:    date and time of the last uploade
    """
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))

    if options.get('init'):
        if os.path.exists(os.path.join(package_dir, SETTINGS_FILENAME)) and \
                click.confirm('Are you sure you want to overwrite the current settingsfile '
                              '(old settings will be a backup)?'):
            copy_path(os.path.join(package_dir, SETTINGS_FILENAME),
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
        settings['python_version'] = click.prompt('Python version (choose from: {})'.
                                                  format(settings.get('pyversions')), default='3.5')
        settings['exclude_paths'] = click.prompt("Exclude additional paths from kecpkg (eg. 'data, input')",
                                                 default=settings.get('exclude_paths', ''),
                                                 value_proc=process_additional_exclude_paths)
        save_settings(settings, package_dir=package_dir)

    if options.get('verbose'):
        for k, v in settings.items():
            echo_info("  {}: '{}'".format(k, v))

    if not options.get('interactive'):
        echo_success('Settings file identified and correct')


def process_additional_exclude_paths(raw_value):
    """Process additional list of exclude paths and return a list"""
    assert isinstance(raw_value, str), "The value should be a string, got: {}".format(type(raw_value))

    pathlist = []
    raw_pathlist = raw_value.split(',')
    for raw_path in raw_pathlist:
        pathlist.append(raw_path.strip())
    return pathlist
