import shutil
import subprocess
import sys

import os
from hatch.utils import get_proper_python, NEED_SUBPROCESS_SHELL

from kecpkg.files.rendering import render_to_file
from kecpkg.utils import ensure_dir_exists, snake_case


def create_package(pkg_dir, package_name, settings):
    """
    Create the package directory

    pkg_dir
    +-- README.md
    +-- requirements.txt
    +-- package_info.json
    +-- package_name
        +-- __init__.py
        +-- main.py


    :param kecpkg_dir: root dir where to create the kecpkg
    :param package_name: name of the package
    :param settings: settings dict
    """
    ensure_dir_exists(pkg_dir)
    render_to_file('readme.md', content=settings, target_dir=pkg_dir)
    render_to_file('requirements.txt', content=settings, target_dir=pkg_dir)
    render_to_file('package_info.json', content={'requirements_txt': 'requirements.txt'}, target_dir=pkg_dir)
    render_to_file('script.py', content=settings, target_dir=pkg_dir)


def create_venv(pkg_dir, settings, pypath=None, use_global=False, verbose=False):
    """
    Create the virtual environment in `venv` for the package.

    The virtual environment path name can be set in the settings.

    pkg_dir
    +-- venv  (the virtual environment based on the choosen python version)
        +-- ...

    :param pkg_dir:
    :param settings:
    """
    venv_dir = os.path.join(pkg_dir, settings.get('venv_dir'))

    command = [sys.executable, '-m', 'virtualenv', venv_dir,
               '-p', pypath or shutil.which(get_proper_python())]
    if use_global:  # no cov
        command.append('--system-site-packages')
    if not verbose:  # no cov
        command.append('-qqq')
    result = subprocess.run(command, shell=NEED_SUBPROCESS_SHELL)
    return result.returncode

