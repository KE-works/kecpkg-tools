import json
import os
from collections import OrderedDict
from copy import deepcopy

from atomicwrites import atomic_write

from kecpkg.utils import ensure_dir_exists, create_file, get_package_dir

SETTINGS_FILENAME = '.kecpkg_settings.json'
SETTINGS_FILE = os.path.join(os.getcwd(), SETTINGS_FILENAME)

DEFAULT_SETTINGS = OrderedDict([
    ('version', '0.0.1'),
    ('pyversions', ['2.7', '3.5']),
    ('python_version', '3.5'),
    ('venv_dir', 'venv'),
    ('entrypoint_script', 'script'),
    ('entrypoint_func', 'main'),
    ('build_dir', 'dist'),
    ('requirements_filename', 'requirements.txt')
])

EXCLUDE_DIRS_IN_BUILD = (
    'venv', 'dist', '.idea', '.tox', '.cache', 'venv*', '.env', '__pycache__', 'develop-eggs', 'downloads', 'eggs',
    'lib', 'lib64', 'sdist', 'wheels', '.hypothesis', '.ipynb_checkpoints', '.mypy_cache'
)

EXCLUDE_PATHS_IN_BUILD = (
    '.gitignore', '*.pyc', '*.pyo', '*.pyd', '*$py.class', '*.egg-info', '.installed.cfg', '.coveragerc', '*.egg',
    'pip-log.txt', '*.log', 'pip-delete-this-directory.txt', '.coverage*', 'nosetests.xml', 'coverage.xml', '*.cover',
    'env.bak', 'venv.bak', 'pip-selfcheck.json', '*.so'
)

EXCLUDE_IN_BUILD = EXCLUDE_DIRS_IN_BUILD + EXCLUDE_PATHS_IN_BUILD


def copy_default_settings():
    """Copy the default settings to a new dict."""
    return deepcopy(DEFAULT_SETTINGS)


def load_settings(lazy=False, package_dir=None):
    """
    Load settings from disk.

    :param lazy: (optional) does lazy loading (default to False)
    :param package_dir: (optional) loads the settings from a package dir
    :return: settings dictionary
    """
    settings_filepath = get_settings_filepath(package_dir)
    if lazy and not os.path.exists(settings_filepath):
        return {}
    with open(settings_filepath, 'r') as f:
        return json.loads(f.read(), object_pairs_hook=OrderedDict)


def get_settings_filepath(package_dir=None):
    """
    Return the filepath of the settings file.

    :param package_dir: (optional) Package dir to search in
    :return: path tot the settings file
    """
    if package_dir:
        return os.path.join(package_dir, SETTINGS_FILENAME)
    else:
        return SETTINGS_FILE


def save_settings(settings, package_dir=None):
    """
    Save settings in path (in the package).

    :param settings: settings to save
    :param package_dir: (optional) package_dir to save to
    :return: None
    """
    if settings.get('package_name') and not package_dir:
        package_dir = get_package_dir(settings.get('package_name'))
    settings_filepath = get_settings_filepath(package_dir)

    ensure_dir_exists(os.path.dirname(settings_filepath))
    with atomic_write(settings_filepath, overwrite=True) as f:
        f.write(json.dumps(settings, indent=4))


def restore_settings(package_dir=None):
    """
    Restore settings to their defaults (overwrite old settings).

    :param package_dir: (optional) package dir to search the settings file in
    :return: None
    """
    settings_filepath = get_settings_filepath(package_dir)

    create_file(settings_filepath)
    settings = copy_default_settings()
    if package_dir:
        package_name = os.path.dirname(package_dir)
        settings['package_name'] = package_name
    save_settings(settings=settings)
