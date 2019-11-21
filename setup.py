from io import open

import os
from setuptools import find_packages, setup

PACKAGE_NAME = 'kecpkg'
HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

ABOUT = {}
with open(os.path.join(PACKAGE_NAME, '__init__.py'), 'r') as f:
    exec(f.read(), ABOUT)

setup(
    name='kecpkg-tools',
    version=ABOUT.get('__version__'),
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jochem Berends',
    author_email='jochem.berends@ke-works.com',
    maintainer='Jochem Berends',
    maintainer_email='jochem.berends@ke-works.com',
    url='https://github.com/jberends/kecpkg-tools',
    license='Apache-2.0',

    keywords=(
        'python',
        'package tools',
        'pykechain',
        'KE-chain',
        'Services Integration Module',
        'SIM',
        'KECPKG',
        'GPG'
    ),

    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),

    install_requires=(
        'click',
        'atomicwrites',
        'jinja2',
        'pykechain>=3.0',
        'appdirs',
        'tabulate',
        'python-gnupg'
    ),

    tests_require=(
        'coverage',
        'pytest',
        'flake8',
        'virtualenv'
    ),

    packages=find_packages(exclude=['tests']),

    # to include the templates in the bdist wheel, we need to add package_data here
    package_data={
        'kecpkg': ['files/templates/*.template',
                   'files/templates/.*.template']
    },

    entry_points={
        'console_scripts': (
            'kecpkg = kecpkg.cli:kecpkg',
        ),
    }
)
