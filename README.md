# kecpkg-tools

[![PyPI](https://img.shields.io/pypi/v/kecpkg-tools.svg)](https://pypi.python.org/pypi/kecpkg-tools)
[![Snap Status](https://build.snapcraft.io/badge/KE-works/kecpkg-tools.svg)](https://build.snapcraft.io/user/KE-works/kecpkg-tools)
[![PyPI - Status](https://img.shields.io/pypi/status/kecpkg-tools.svg)](https://pypi.python.org/pypi/kecpkg-tools)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kecpkg-tools.svg)
[![Travis Build](https://travis-ci.org/KE-works/kecpkg-tools.svg?branch=master)](https://travis-ci.org/KE-works/kecpkg-tools)
[![Join the chat at https://gitter.im/KE-works/pykechain](https://badges.gitter.im/KE-works/pykechain.svg)](https://gitter.im/KE-works/pykechain?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


## Usage

kecpkg-tools provide a set of tools to easily create KE-chain packages.
These are executable python scripts aimed for execution on the KE-chain
SIM platform.

It requires normal user access to a [KE-chain](http://www.ke-chain.com)
instance for it to work. KE-chain is the flexible engineering platform
of [KE-works](http://www.ke-works.com).

## See Also

KE-chain packages for SIM are used in combination with
[pykechain](https://github.com/KE-works/pykechain), the open source
KE-chain python api.

## Installation

### Installation with pip
kecpkg-tools is distributed on [PyPI](https://pypi.org) as a universal
wheel and is available on Linux/macOS and Windows and supports Python
2.7/3.4+ and PyPy.

```bash
$ pip install --user --upgrade kecpkg-tools
```

or when pip is not installed on the system

```bash
$ python3 -m pip install --user --upgrade kecpkg-tools
```

### Installation using snap (beta)

When on a linux platform, you may use the snapstore to install kecpkg automatically and
keep it up to date to the latest and greated.

```bash
$ sudo snap install kecpkg --devmode --dangerous
```

Any feedback is appreciated as we are in beta mode for publishing `kecpkg` on the snapstore.

## License

kecpkg-tools is distributed under the terms of the [Apache License,
Version 2.0](https://choosealicense.com/licenses/apache-2.0).
