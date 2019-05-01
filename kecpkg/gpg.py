import hashlib
import os
import subprocess

from kecpkg.settings import GNUPG_KECPKG_HOME
from kecpkg.utils import ON_LINUX, ON_WINDOWS, ON_MACOS, echo_failure, read_chunks


def hash_of_file(path, algorithm='sha256'):
    """Return the hash digest of a file."""
    with open(path, 'rb') as archive:
        hash = hashlib.new(algorithm)
        for chunk in read_chunks(archive):
            hash.update(chunk)
    return hash.hexdigest()


__gpg = None


def get_gpg():
    """Return the GPG objects instantiated with custom KECPKG keyring in custom KECPKG GNUPG home."""
    global __gpg
    if not __gpg:
        import logging
        import gnupg
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('gnupg')
        gpg_bin='gpg'
        if ON_LINUX:
            gpg_bin = subprocess.getoutput('which gpg')
        if ON_WINDOWS:
            gpg_bin = 'C:\Program Files\GnuPG\gpg'
        elif ON_MACOS:
            gpg_bin = '/usr/local/bin/gpg'
        if not os.path.exists(gpg_bin):
            echo_failure("Unable to detect installed GnuPG executable. Ensure you have it installed. "
                         "We checked: '{}'".format(gpg_bin))

        __gpg = gnupg.GPG(gpgbinary=gpg_bin, gnupghome=GNUPG_KECPKG_HOME)

    return __gpg
