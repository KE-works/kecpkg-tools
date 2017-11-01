import os
import re
import shutil
import sys
from urllib.request import urlopen

from kecpkg.commands.utils import echo_warning, echo_failure, echo_info


def ensure_dir_exists(d):
    if not os.path.exists(d):
        os.makedirs(d)


def create_file(filepath, content=None):
    ensure_dir_exists(os.path.dirname(os.path.abspath(filepath)))
    with open(filepath, 'w') as fd:
        os.utime(filepath, times=None)
        if content:
            fd.write(content)


def download_file(url, fname):
    req = urlopen(url)
    with open(fname, 'wb') as f:
        while True:
            chunk = req.read(16384)
            if not chunk:
                break
            f.write(chunk)
            f.flush()


def copy_path(path, d):
    if os.path.isdir(path):
        shutil.copytree(
            path,
            os.path.join(d, basepath(path)),
            copy_function=shutil.copy
        )
    else:
        shutil.copy(path, d)


def remove_path(path):
    try:
        shutil.rmtree(path)
    except (FileNotFoundError, OSError):
        try:
            os.remove(path)
        except (FileNotFoundError, PermissionError):
            pass


def basepath(path):
    return os.path.basename(os.path.normpath(path))


def normalise_name(package_name):
    return re.sub(r"[-_. ]+", "_", package_name).lower()


def get_package_dir(package_name=None):
    package_dir = package_name and os.path.join(os.getcwd(), package_name) or os.getcwd()

    try:
        from kecpkg.settings import load_settings
        # load settings just to test that we are inside a package dir
        load_settings(package_dir=package_dir)
        return package_dir
    except FileNotFoundError:
        echo_warning('Cannot find settings in path `{}`...'.format(package_dir))
        if os.path.exists(os.path.join(package_dir, 'package_info.json')):
            return package_dir
        else:
            from kecpkg.settings import SETTINGS_FILENAME
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
