from __future__ import print_function

import os
import subprocess
import sys

import six

from kecpkg.files.rendering import render_to_file
from kecpkg.utils import (ensure_dir_exists, get_proper_python, NEED_SUBPROCESS_SHELL, venv,
                          echo_success, echo_failure, echo_info)


def create_package(package_dir, settings):
    """
    Create the package directory.

    package_name  (or package_dir)
    +-- README.md
    +-- requirements.txt
    +-- package_info.json
    +-- main.py  (settable with settings['entrypoint_script']

    :param package_dir: the full path to the package dir
    :param settings: settings dict
    """
    ensure_dir_exists(package_dir)
    render_to_file('README.md', content=settings, target_dir=package_dir)
    render_to_file('requirements.txt', content=settings, target_dir=package_dir)
    render_to_file('package_info.json', content=dict(requirements_txt='requirements.txt',
                                                     entrypoint_script=settings.get('entrypoint_script'),
                                                     entrypoint_func=settings.get('entrypoint_func')),
                   target_dir=package_dir)
    render_to_file('.gitignore', content=dict(), target_dir=package_dir)
    render_to_file('.env', content=dict(), target_dir=package_dir)

    # runconfigurations
    run_configurations_path = os.path.join(package_dir, '.idea', 'runConfigurations')
    ensure_dir_exists(run_configurations_path)
    render_to_file('Upload_the_kecpkg.xml', content=dict(), target_dir=run_configurations_path)
    render_to_file('Build_the_kecpkg.xml', content=dict(), target_dir=run_configurations_path)

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
    :param settings: the settings dict (including the venv_dir name to create the right venv)
    :param pypath: absolute path to the python binary interpreter to create the virtual environment with
    :param use_global: Use global sysem site packages when creating virtual environment (default False)
    :param verbose: Use verbosity (default False)
    """
    venv_dir = os.path.join(package_dir, settings.get('venv_dir'))

    if not pypath:
        from distutils.spawn import find_executable
        pypath = find_executable(get_proper_python())

    command = [sys.executable, '-m', 'virtualenv', venv_dir, '-p', pypath]
    if use_global:  # no cov
        command.append('--system-site-packages')
    if not verbose:  # no cov
        command.append('-qqq')
    if six.PY3:
        result = subprocess.run(command, shell=NEED_SUBPROCESS_SHELL)
        return result.returncode
    elif six.PY2:
        result = subprocess.check_output(command, shell=NEED_SUBPROCESS_SHELL)
        return result and 0 or -1


def pip_install_venv(package_dir, settings, verbose=False):
    """
    Install requirements into the virtual environment.

    :param package_dir: the full path to the package directory
    :param settings: the settings dict (incluing the venv_dir name)
    :param verbose: (optional) be more verbose if set to True, defaults to False
    """
    venv_dir = os.path.join(package_dir, settings.get('venv_dir'))
    if not os.path.exists(venv_dir):
        echo_failure('virtual environment directory `{}` does not exists, nothing to install'.format(venv_dir))
        sys.exit(1)

    if not os.path.exists(os.path.join(package_dir, settings.get('requirements_filename'))):
        echo_failure('could not find requirements.txt to install, check if `{}` exists or update settings'.format(
            settings.get('requirements_filename')))
        sys.exit(1)

    install_command = [sys.executable, '-m', 'pip', 'install', '-r',
                       os.path.join(package_dir, settings.get('requirements_filename'))]

    if not verbose:  # no cov
        install_command.append('-qqq')

    with venv(venv_dir):
        echo_info('Installing requirements from `{}` into the virtual environment `{}`'.
                  format(settings.get('requirements_filename'), settings.get('venv_dir')))
        result = None
        if six.PY3:
            result = subprocess.run(install_command, shell=NEED_SUBPROCESS_SHELL)
            return result.returncode
        elif six.PY2:
            result = subprocess.check_output(install_command, shell=NEED_SUBPROCESS_SHELL)
            return result and 0 or -1

    if result:
        echo_success(str(result))

    return result.returncode
