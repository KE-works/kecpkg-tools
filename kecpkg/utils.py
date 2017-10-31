import os
import re
import shutil
from urllib.request import urlopen


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
