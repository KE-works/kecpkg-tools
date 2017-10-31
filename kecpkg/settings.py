import json
import os

from copy import deepcopy

from kecpkg.utils import ensure_dir_exists, create_file

from atomicwrites import atomic_write
from collections import OrderedDict

SETTINGS_FILE = os.path.join(os.getcwd(), 'kecpkg_settings.json')

DEFAULT_SETTINGS = OrderedDict([
    ('pyversions', ['2.7', '3.5']),
    ('python_version', '3.5')
])


def copy_default_settings():
    return deepcopy(DEFAULT_SETTINGS)


def load_settings(lazy=False):
    if lazy and not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, 'r') as f:
        return json.loads(f.read(), object_pairs_hook=OrderedDict)


def save_settings(settings):
    ensure_dir_exists(os.path.dirname(SETTINGS_FILE))
    with atomic_write(SETTINGS_FILE, overwrite=True) as f:
        f.write(json.dumps(settings, indent=4))


def restore_settings():
    create_file(SETTINGS_FILE)
    save_settings(DEFAULT_SETTINGS)
