import json
import os
from collections import OrderedDict
from copy import deepcopy

from atomicwrites import atomic_write

from kecpkg.utils import ensure_dir_exists, create_file

SETTINGS_FILENAME = '.kecpkg_settings.json'
SETTINGS_FILE = os.path.join(os.getcwd(), SETTINGS_FILENAME)

DEFAULT_SETTINGS = OrderedDict([
    ('version', '0.0.1'),
    ('pyversions', ['2.7', '3.5']),
    ('python_version', '3.5'),
    ('venv_dir', 'venv'),
    ('entrypoint_script', 'script'),
    ('entrypoint_func', 'main')
])


def copy_default_settings():
    return deepcopy(DEFAULT_SETTINGS)


def load_settings(lazy=False, package_dir=None):
    settings_filepath = get_settings_filepath(package_dir)
    if lazy and not os.path.exists(settings_filepath):
        return {}
    with open(settings_filepath, 'r') as f:
        return json.loads(f.read(), object_pairs_hook=OrderedDict)


def get_settings_filepath(package_dir=None):
    if package_dir:
        return os.path.join(package_dir, SETTINGS_FILENAME)
    else:
        return SETTINGS_FILE


def save_settings(settings, package_dir=None):
    """
    Saving settings in path (either global, otherwise in the package)

    :param settings: settings to save
    :param package_dir: (optional) package_dir to save to
    """
    settings_filepath = get_settings_filepath(package_dir)

    ensure_dir_exists(os.path.dirname(settings_filepath))
    with atomic_write(settings_filepath, overwrite=True) as f:
        f.write(json.dumps(settings, indent=4))


def restore_settings(package_dir=None):
    settings_filepath = get_settings_filepath(package_dir)

    create_file(settings_filepath)
    save_settings(settings=DEFAULT_SETTINGS)
