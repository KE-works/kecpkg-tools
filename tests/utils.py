import os
import socket
from contextlib import contextmanager

from unittest import TestCase

import pytest
import six
from click.testing import CliRunner


class BaseTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def assertExists(self, path):
        self.assertTrue(os.path.exists(path), "Path `{}` does not exists".format(path))

@contextmanager
def temp_chdir(cwd=None):
    if six.PY3:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(prefix="kecpkg_") as tempwd:
            origin = cwd or os.getcwd()
            os.chdir(tempwd)

            try:
                yield tempwd if os.path.exists(tempwd) else ''
            finally:
                os.chdir(origin)
    else:
        from tempfile import mkdtemp
        tempwd = mkdtemp(prefix="kecpkg_")
        origin=cwd or os.getcwd()
        os.chdir(tempwd)
        try:
            yield tempwd if os.path.exists(tempwd) else ''
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

def touch_file(path):
    """Create an empty file in path.

    :param path: path (filename)
    """
    with open(path, 'a'):
        os.utime(path, None)



requires_internet = pytest.mark.skipif(
    not connected_to_internet(), reason='Not connected to internet'
)
