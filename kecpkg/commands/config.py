import click
import os

from kecpkg.commands.utils import CONTEXT_SETTINGS, echo_info, echo_success
from kecpkg.settings import load_settings
from kecpkg.utils import get_package_dir


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Finds and updated the configuration of the kecpkg")
@click.argument('package', required=False)
@click.option('--interactive', '-i', is_flag=True, help="interactive mode; guide me through the upload")
@click.option('--verbose', '-v', is_flag=True, help="be more verbose (print settings)")
def config(package, **options):
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))
    settings = load_settings(package_dir=package_dir)

    if options.get('verbose'):
        for k,v in settings.items():
            echo_info("  {}: '{}'".format(k, v))

    if not options.get('interactive'):
        echo_success('Settings file identified and correct')