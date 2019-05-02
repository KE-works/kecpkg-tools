import hashlib
import logging
import os
import subprocess

import gnupg

from kecpkg.settings import GNUPG_KECPKG_HOME
from kecpkg.utils import ON_LINUX, ON_WINDOWS, ON_MACOS, echo_failure, read_chunks

LOGLEVEL = logging.INFO


def hash_of_file(path, algorithm='sha256'):
    """Return the hash digest of a file."""
    with open(path, 'rb') as archive:
        hash = hashlib.new(algorithm)
        for chunk in read_chunks(archive):
            hash.update(chunk)
    return hash.hexdigest()


__gpg = None  # type: gnupg.GPG


def get_gpg():
    # type: () -> gnupg.GPG
    """Return the GPG objects instantiated with custom KECPKG keyring in custom KECPKG GNUPG home."""
    global __gpg
    if not __gpg:
        import gnupg
        logging.basicConfig(level=LOGLEVEL)
        logging.getLogger('gnupg')
        gpg_bin = 'gpg'
        if ON_LINUX:
            gpg_bin = subprocess.getoutput('which gpg')
        if ON_WINDOWS:
            gpg_bin = 'C:\Program Files\GnuPG\gpg'
        elif ON_MACOS:
            gpg_bin = '/usr/local/bin/gpg'
        if not os.path.exists(gpg_bin):
            echo_failure("Unable to detect installed GnuPG executable. Ensure you have it installed. "
                         "We checked: '{}'".format(gpg_bin))
            echo_failure("- For Linux please install GnuPG using your package manager. In Ubuntu/Debian this can be "
                         "achieved with `sudo apt install gnupg`.")
            echo_failure("- For Mac OSX please install GnuPG using `brew install gpg`.")
            echo_failure("- For Windows please install GnuPG using the downloads via: https://gnupg.org/download/")

        __gpg = gnupg.GPG(gpgbinary=gpg_bin, gnupghome=GNUPG_KECPKG_HOME)

    return __gpg
