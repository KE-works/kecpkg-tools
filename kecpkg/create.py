import os
import shutil
import subprocess
import sys

from hatch.utils import get_proper_python, NEED_SUBPROCESS_SHELL

from kecpkg.files.rendering import render_to_file
from kecpkg.utils import ensure_dir_exists


def create_package(package_dir, settings):
    """
    Create the package directory

    package_name  (or package_dir)
    +-- README.md
    +-- requirements.txt
    +-- package_info.json
    +-- main.py  (settable with settings['entrypoint_script']

    :param package_dir: the full path to the package dir
    :param settings: settings dict
    """
    ensure_dir_exists(package_dir)
    render_to_file('readme.md', content=settings, target_dir=package_dir)
    render_to_file('requirements.txt', content=settings, target_dir=package_dir)
    render_to_file('package_info.json', content=dict(requirements_txt='requirements.txt',
                                                     entrypoint_script=settings.get('entrypoint_script'),
                                                     entrypoint_func=settings.get('entrypoint_func')),
                   target_dir=package_dir)
    script_filename = '{}.py'.format(settings.get('entrypoint_script'))
    render_to_file(script_filename, content=settings, template='script.py.template', target_dir=package_dir)


def create_venv(package_dir, settings, pypath=None, use_global=False, verbose=False):
    """
    Create the virtual environment in `venv` for the package.

    The virtual environment path name can be set in the settings.

    package_dir
    +-- venv  (the virtual environment based on the choosen python version)
        +-- ...

    :param package_dir: the full path to the package directory
    :param settings: the settings dict (including the venv_dir name to create the right venv
    """
    venv_dir = os.path.join(package_dir, settings.get('venv_dir'))

    command = [sys.executable, '-m', 'virtualenv', venv_dir,
               '-p', pypath or shutil.which(get_proper_python())]
    if use_global:  # no cov
        command.append('--system-site-packages')
    if not verbose:  # no cov
        command.append('-qqq')
    result = subprocess.run(command, shell=NEED_SUBPROCESS_SHELL)
    return result.returncode
