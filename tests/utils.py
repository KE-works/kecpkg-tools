import os
import socket
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import pytest


@contextmanager
def temp_chdir(cwd=None):
    with TemporaryDirectory() as d:
        origin = cwd or os.getcwd()
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