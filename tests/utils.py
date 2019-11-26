import os
import socket
from contextlib import contextmanager
from unittest import TestCase

import six
from click.testing import CliRunner


class BaseTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def assertExists(self, path):
        self.assertTrue(os.path.exists(path), "Path `{}` does not exists".format(path))


def is_travis():
    """Predicate to determine if the test is running in the context of Travis."""
    return "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"


def is_python27():
    """Predicate to determine if the runtime version of python is version 2."""
    import sys
    return sys.version_info <= (2, 7)


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
        origin = cwd or os.getcwd()
        os.chdir(tempwd)
        try:
            yield tempwd if os.path.exists(tempwd) else ''
        finally:
            os.chdir(origin)


def touch_file(path):
    """Create an empty file in path.

    :param path: path (filename)
    """
    with open(path, 'a'):
        os.utime(path, None)


def connected_to_internet():  # no cov
    # type: () -> bool
    """If the system is connected to the internet."""
    if running_on_ci():
        return True
    try:
        # Test availability of DNS first
        host = socket.gethostbyname('ke-works.com')
        # Test connection
        socket.create_connection((host, 80), 2)
        return True
    except:
        return False


def running_on_ci():  # no cov
    # type: () -> bool
    """If the system is running on a CI platform."""
    if os.environ.get('CI') or os.environ.get('TRAVIS') or os.environ.get('GITHUB_ACTIONS'):
        return True
    return False
