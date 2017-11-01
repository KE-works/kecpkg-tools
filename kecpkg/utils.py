import os
import re
import shutil
import sys
from urllib.request import urlopen

from kecpkg.commands.utils import echo_warning, echo_failure, echo_info


def ensure_dir_exists(d):
    """Ensure that directory exists, otherwise make directory."""
    if not os.path.exists(d):
        os.makedirs(d)


def create_file(filepath, content=None, overwrite=True):
    """
    Create file and optionally fill it with content.

    Will overwrite file already in place if overwrite flag is set

    :param filepath: full path to a file to create
    :param content:
    :return:
    """
    ensure_dir_exists(os.path.dirname(os.path.abspath(filepath)))
    # if overwrite is set to True overwrite file, otherwise if file exist, exit.

    if not os.path.exists(filepath) or (os.path.exists(filepath) and overwrite):
        with open(filepath, 'w') as fd:
            os.utime(filepath, times=None)
            if content:
                fd.write(content)
    else:
        echo_failure("File '{}' already exists.".format(filepath))
        sys.exit(1)


def download_file(url, filepath):
    """
    Download file from url and save to disk as filename.

    :param url: url to download file from
    :param filepath: filename to write to
    """
    req = urlopen(url)
    with open(filepath, 'wb') as f:
        while True:
            chunk = req.read(16384)
            if not chunk:
                break
            f.write(chunk)
            f.flush()


def copy_path(sourcepath, destpath):
    """
    Copy path.

    :param sourcepath: source path to copy from, if dir, copy subtree
    :param destpath: destination path to copy to
    """
    if os.path.isdir(sourcepath):
        shutil.copytree(
            sourcepath,
            os.path.join(destpath, basepath(sourcepath)),
            copy_function=shutil.copy
        )
    else:
        shutil.copy(sourcepath, destpath)


def remove_path(path):
    """
    Remove directory structure.

    :param path: path to remove
    """
    try:
        shutil.rmtree(path)
    except (FileNotFoundError, OSError):
        try:
            os.remove(path)
        except (FileNotFoundError, PermissionError):
            pass


def basepath(path):
    """Get full basepath from path."""
    return os.path.basename(os.path.normpath(path))


def normalise_name(raw_name):
    """
    Normalise the name to be used in python package allowable names.

    conforms to PEP-423 package naming conventions

    :param raw_name: raw string
    :return: normalised string
    """
    return re.sub(r"[-_. ]+", "_", raw_name).lower()


def get_package_dir(package_name=None, fail=True):
    """
    Check and retrieve the package directory.

    :param package_name: (optional) package name
    :param fail: (optional, default=True) fail hard with exit when no package dir found
    :return: full path name to the package directory
    """

    def _inner(d):
        from kecpkg.settings import load_settings
        try:
            # load settings just to test that we are inside a package dir
            load_settings(package_dir=d)
            return d
        except FileNotFoundError:
            if os.path.exists(os.path.join(d, 'package_info.json')):
                return d
            else:
                return None

    package_dir = _inner(os.getcwd())
    if not package_dir:
        package_dir = _inner(os.path.join(os.getcwd(), package_name))
    if not package_dir:
        package_dir = _inner(package_name)
    if not package_dir:
        from kecpkg.settings import SETTINGS_FILENAME
        echo_failure('This does not seem to be a package in path `{}` - please check that there is a '
                     '`package_info.json` or a `{}`'.format(package_dir, SETTINGS_FILENAME))
        if fail:
            sys.exit(1)
    else:
        return package_dir


def get_package_name():
    """
    Provide the name of the package (in current dir)

    :param fail: ensure that directory search does not fail in a exit.
    :return: package name or None
    """
    package_dir = get_package_dir(fail=False)
    if package_dir:
        return os.path.basename(package_dir)
    else:
        return None


def get_artifacts_on_disk(root_path, exclude_paths=('venv', 'dist'), verbose=False):
    """
    Retrieve all artifacts on disk.

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
