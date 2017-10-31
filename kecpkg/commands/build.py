import os
import sys
from zipfile import ZipFile

import click as click

from kecpkg.commands.utils import CONTEXT_SETTINGS, echo_info, echo_failure, echo_warning
from kecpkg.settings import load_settings, SETTINGS_FILENAME
from kecpkg.utils import ensure_dir_exists, remove_path, copy_path


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Build the package and create a kecpkg file")
@click.argument('package', required=False)
@click.option('--clean', 'clean_first', is_flag=True, help='Remove build artifacts before building')
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def build(package=None, **options):
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))
    settings = load_settings(package_dir=package_dir)

    build_dir = os.path.join(package_dir, 'dist')

    if options.get('clean_first'):
        remove_path(build_dir)
    ensure_dir_exists(build_dir)



    build_package(package_dir, build_dir, settings, verbose=options.get('verbose'))




def build_package(package_dir, build_dir, settings, verbose=False):
    artifacts = get_artifacts_on_disk(package_dir, verbose=False)
    dist_filename = '{}-{}-py{}.zip'.format(settings.get('package_name'), settings.get('version'), settings.get('python_version'))
    echo_info('Creating package name `{}`'.format(dist_filename))

    with ZipFile(os.path.join(build_dir, dist_filename), 'x') as dist_zip:
        for artifact in artifacts:
            dist_zip.write(os.path.join(package_dir, artifact), arcname=artifact)






def get_package_dir(package_name=None):
    package_dir = package_name and os.path.join(os.getcwd(), package_name) or os.getcwd()

    try:
        settings = load_settings(package_dir=package_dir)
        return package_dir
    except FileNotFoundError:
        echo_warning(
            'Cannot find settings in path `{}`...'.format(package_dir))
        if os.path.exists(os.path.join(package_dir, 'package_info.json')):
            return package_dir
        else:
            echo_failure('This does not seem to be a package in path `{}` - please check that there is a '
                         '`package_info.json` or a `{}`'.format(package_dir, SETTINGS_FILENAME))
            sys.exit(1)


def get_artifacts_on_disk(root_path, exclude_paths=('venv', 'dist'), verbose=False):
    """
    retrieve all artifacts on disk

    :param root_path: root_path to collect all artifacts from
    :param exclude_paths: (optional) directory names and filenames to exclude
    :return: dictionary with {'property_id': ['attachment_path1', ...], ...}
    """
    if not os.path.exists(root_path):
        echo_failure("The root path: '{}' does not exist".format(root_path))
        sys.exit(1)

    # getting all attachments
    artifacts = []
    for root, dirs, filenames in os.walk(root_path):
        # remove the excluded paths
        for exclude_path in exclude_paths:
            if exclude_path in dirs:
                dirs.remove(exclude_path)

        for filename in filenames:
            full_artifact_subpath = '{}{}{}'.format(root, os.path.sep, filename). \
                replace('{}{}'.format(root_path, os.path.sep), '')
            artifacts.append(full_artifact_subpath)
            if verbose:
                echo_info('Found `{}`'.format(full_artifact_subpath))
    if verbose:
        echo_info('{}'.format(artifacts))
    return artifacts
