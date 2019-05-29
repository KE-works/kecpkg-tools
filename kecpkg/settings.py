import json
import os
from collections import OrderedDict
from copy import deepcopy

import sys

from appdirs import user_data_dir
from atomicwrites import atomic_write

from kecpkg.utils import ensure_dir_exists, create_file, get_package_dir, echo_failure

SETTINGS_FILENAME = '.kecpkg_settings.json'
SETTINGS_FILE = os.path.join(os.getcwd(), SETTINGS_FILENAME)
ARTIFACTS_FILENAME = 'ARTIFACTS'
ARTIFACTS_SIG_FILENAME = 'ARTIFACTS.SIG'

# using the appdirs.user_data_dir to manage user data on various platforms.
GNUPG_KECPKG_HOME = os.path.join(user_data_dir('kecpkg', 'KE-works BV'), '.gnupg')

DEFAULT_SETTINGS = OrderedDict([
    ('version', '0.0.1'),
    ('pyversions', ['2.7', '3.5', '3.6']),
    ('python_version', '3.5'),
    ('venv_dir', 'venv'),
    ('entrypoint_script', 'script'),
    ('entrypoint_func', 'main'),
    ('build_dir', 'dist'),
    ('requirements_filename', 'requirements.txt'),
    ('artifacts_filename', ARTIFACTS_FILENAME),
    ('artifacts_sig_filename', ARTIFACTS_SIG_FILENAME),
    ('hash_algorithm', 'sha256')
])

EXCLUDE_DIRS_IN_BUILD = [
    'venv', 'dist', '.idea', '.tox', '.cache', '.git', 'venv*', '_venv*', '.env', '__pycache__', 'develop-eggs',
    'downloads', 'eggs', 'lib', 'lib64', 'sdist', 'wheels', '.hypothesis', '.ipynb_checkpoints', '.mypy_cache',
    '.vscode'
]

EXCLUDE_PATHS_IN_BUILD = [
    '.gitignore', '*.pyc', '*.pyo', '*.pyd', '*$py.class', '*.egg-info', '.installed.cfg', '.coveragerc', '*.egg',
    'pip-log.txt', '*.log', 'pip-delete-this-directory.txt', '.coverage*', 'nosetests.xml', 'coverage.xml', '*.cover',
    'env.bak', 'venv.bak', 'pip-selfcheck.json', '*.so', '*-dist', '.*.swp', '*.asc'
]

EXCLUDE_IN_BUILD = EXCLUDE_DIRS_IN_BUILD + EXCLUDE_PATHS_IN_BUILD


def copy_default_settings():
    """Copy the default settings to a new dict."""
    return deepcopy(DEFAULT_SETTINGS)


def load_settings(lazy=False, package_dir=None, settings_filename=None):
    """
    Load settings from disk.

    :param lazy: (optional) does lazy loading (default to False)
    :param package_dir: (optional) loads the settings from a package dir
    :param settings_filename: (optional) pathname of the file where the settings are stored
    :return: settings dictionary
    """
    settings_filepath = get_settings_filepath(package_dir, settings_filename)
    if lazy and not os.path.exists(settings_filepath):
        return {}
    elif not os.path.exists(settings_filepath):
        echo_failure('Could not find a settingsfile in path: {}'.format(settings_filepath))
        sys.exit(404)
    else:
        with open(settings_filepath, 'r') as f:
            return json.loads(f.read(), object_pairs_hook=OrderedDict)


def get_settings_filepath(package_dir=None, settings_filename=SETTINGS_FILENAME):
    """
    Return the filepath of the settings file.

    :param package_dir: (optional) Package dir to search in
    :param settings_filename: (optional) pathname of the file where the settings are stored
    :return: path tot the settings file
    """
    if not settings_filename:
        settings_filename = SETTINGS_FILENAME
    if package_dir:
        return os.path.join(package_dir, settings_filename)
    else:
        return SETTINGS_FILE


def save_settings(settings, package_dir=None, settings_filename=None):
    """
    Save settings in path (in the package).

    :param settings: settings to save
    :param settings_filename: (optional) pathname of the file where the settings are stored
    :param package_dir: (optional) package_dir to save to
    :return: None
    """
    if settings.get('package_name') and not package_dir:
        package_dir = get_package_dir(settings.get('package_name'))
    settings_filepath = get_settings_filepath(package_dir, settings_filename)

    ensure_dir_exists(os.path.dirname(settings_filepath))
    with atomic_write(settings_filepath, overwrite=True) as f:
        f.write(json.dumps(settings, indent=4))


def restore_settings(package_dir=None, settings_filename=None):
    """
    Restore settings to their defaults (overwrite old settings).

    :param package_dir: (optional) package dir to search the settings file in
    :param settings_filename: (optional) pathname of the file where the settings are stored
    :return: None
    """
    settings_filepath = get_settings_filepath(package_dir, settings_filename)

    create_file(settings_filepath)
    settings = copy_default_settings()
    if package_dir:
        package_name = os.path.dirname(package_dir)
        settings['package_name'] = package_name
    save_settings(settings=settings, settings_filename=settings_filename)
