import os
from zipfile import ZipFile

import click as click

from kecpkg.commands.utils import CONTEXT_SETTINGS, echo_info
from kecpkg.settings import load_settings
from kecpkg.utils import ensure_dir_exists, remove_path, get_package_dir, get_artifacts_on_disk


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Build the package and create a kecpkg file")
@click.argument('package', required=False)
@click.option('--clean', '--clear', 'clean_first', is_flag=True, help='Remove build artifacts before building')
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def build(package=None, **options):
    """Build the package and create a kecpkg file."""
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))
    settings = load_settings(package_dir=package_dir)

    # ensure build directory is there
    build_dir = settings.get('build_dir', 'dist')
    build_path = os.path.join(package_dir, build_dir)

    if options.get('clean_first'):
        remove_path(build_path)
    ensure_dir_exists(build_path)

    # do package building
    build_package(package_dir, build_path, settings, verbose=options.get('verbose'))


def build_package(package_dir, build_path, settings, verbose=False):
    """Perform the actual building of the kecpkg zip."""
    additional_exclude_paths = settings.get('exclude_paths')

    artifacts = get_artifacts_on_disk(package_dir, verbose=verbose, additional_exclude_paths=additional_exclude_paths)
    dist_filename = '{}-{}-py{}.kecpkg'.format(settings.get('package_name'), settings.get('version'),
                                               settings.get('python_version'))
    echo_info('Creating package name `{}`'.format(dist_filename))

    with ZipFile(os.path.join(build_path, dist_filename), 'w') as dist_zip:
        for artifact in artifacts:
            dist_zip.write(os.path.join(package_dir, artifact), arcname=artifact)
