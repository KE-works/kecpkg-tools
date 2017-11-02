import os
import socket
from contextlib import contextmanager

from unittest import TestCase

import pytest
import six
from click.testing import CliRunner


class BaseTestCase(TestCase):
    def SetUp(self):
        self.runner = CliRunner()

    def assertExists(self, path):
        self.assertTrue(os.path.exists(path), "Path `{}` does not exists".format(path))

@contextmanager
def temp_chdir(cwd=None):
    if six.PY3:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            origin = cwd or os.getcwd()
            os.chdir(d)

            try:
                yield d if os.path.exists(d) else ''
            finally:
                os.chdir(origin)
    else:
        from tempfile import mkdtemp
        with mkdtemp() as d:
            origin=cwd or os.getcwd()
            os.chdir(d)
            try:
                yield d if os.path.exists(d) else ''
            finally:
                os.chdir(origin)


def connected_to_internet():  # no cov
    if os.environ.get('CI') and os.environ.get('TRAVIS'):
        return True
    try:
        # Test availability of DNS first
        host = socket.gethostbyname('www.google.com')
        # Test connection
        socket.create_connection((host, 80), 2)
        return True
    except:
        return False




requires_internet = pytest.mark.skipif(
    not connected_to_internet(), reason='Not connected to internet'
)