import os
from glob import glob
from io import open
from setuptools import find_packages, setup

with open('kecpkg/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

REQUIRES = ['click', 'atomicwrites', 'jinja2', 'pykechain', 'hatch']
TEST_REQUIRES = ['coverage', 'pytest', 'flake8']

setup(
    name='kecpkg-tools',
    version=version,
    description='',
    long_description=readme,
    author='Jochem Berends',
    author_email='jochem.berends@ke-works.com',
    maintainer='Jochem Berends',
    maintainer_email='jochem.berends@ke-works.com',
    url='https://github.com/jberends/kecpkg-tools',
    license='Apache-2.0',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=REQUIRES,
    tests_require=TEST_REQUIRES,

    packages=find_packages(exclude=['tests']),

    # to include the templates in the bdist wheel, we need to add package_data here
    package_data={
        'kecpkg': ['files/templates/*.template']
    },

    entry_points={
        'console_scripts': (
            'kecpkg = kecpkg.cli:kecpkg',
        ),
    }
)
