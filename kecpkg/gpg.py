import hashlib
import logging
import os
import re
import subprocess
import sys
from datetime import datetime

import gnupg
import six

from kecpkg.settings import GNUPG_KECPKG_HOME
from kecpkg.utils import ON_LINUX, ON_WINDOWS, ON_MACOS, echo_failure, read_chunks, echo_info, ensure_dir_exists

LOGLEVEL = logging.INFO


def hash_of_file(path, algorithm='sha256'):
    """Return the hash digest of a file."""
    with open(path, 'rb') as archive:
        hash = hashlib.new(algorithm)
        for chunk in read_chunks(archive):
            hash.update(chunk)
    return hash.hexdigest()


__gpg = None  # type: gnupg.GPG or None


def has_gpg():
    # type: () -> bool
    """
    Detect the presence of GPG in the OS.

    :returns: true if GPG binary is found on the system, false if not
    """
    try:
        _ = get_gpg()
    except SystemExit:
        return False
    return True


def get_gpg():
    # type: () -> gnupg.GPG
    """Return the GPG objects instantiated with custom KECPKG keyring in custom KECPKG GNUPG home."""
    global __gpg
    if not __gpg:
        if six.PY2:
            echo_failure('Package signing capability is not available in python 2.7. Please use python 3 or greater.')
            sys.exit(1)

        import gnupg
        logging.basicConfig(level=LOGLEVEL)
        logging.getLogger('gnupg')
        gpg_bin = 'gpg'
        if ON_LINUX:
            gpg_bin = subprocess.getoutput('which gpg')
        if ON_WINDOWS:
            bin_path_guesses = ["C:\\Program Files (x86)\\GnuPG\\bin\\gpg.exe",
                                "C:\\Program Files\\GnuPG\\gpg.exe",
                                "C:\\Program Files (x86)\\GnuPG\\gpg.exe",
                                "C:\\Program Files\\GnuPG\\bin\\gpg.exe"]
            gpg_bins = [p for p in bin_path_guesses if os.path.exists(p)]
            if gpg_bins is not None:
                gpg_bin = gpg_bins[0]
            else:
                gpg_bin = bin_path_guesses[0]
        elif ON_MACOS:
            gpg_bin = '/usr/local/bin/gpg'
        if not os.path.exists(gpg_bin):
            echo_failure("Unable to detect installed GnuPG executable. Ensure you have it installed. "
                         "We checked: '{}'".format(gpg_bin))
            echo_failure("- For Linux please install GnuPG using your package manager. In Ubuntu/Debian this can be "
                         "achieved with `sudo apt install gnupg`.")
            echo_failure("- For Mac OSX please install GnuPG using `brew install gpg`.")
            echo_failure("- For Windows please install GnuPG using the downloads via: https://gnupg.org/download/")
            sys.exit(1)

        if not os.path.exists(GNUPG_KECPKG_HOME):
            # create the GNUPG_KECPKG_HOME when not exist, otherwise the GPG will fail
            ensure_dir_exists(GNUPG_KECPKG_HOME)

        __gpg = gnupg.GPG(gpgbinary=gpg_bin, gnupghome=GNUPG_KECPKG_HOME)

    return __gpg


def list_keys(gpg):
    """
    List all keys from the KECPKG keystore and return it as a list of list.

    :param gpg: GPG object
    :return: list of [name, comment, email, expires(str), fingerprint] for each key in the keystore
    """
    result = gpg.list_keys(secret=True)
    key_list = []
    for r in result:
        uids = parse_key_uids(r.get('uids'))
        row = [
            uids.get('name'),
            uids.get('comment'),
            uids.get('email'),
            str(datetime.fromtimestamp(int(r.get('expires')))),
            r.get('fingerprint')
        ]
        key_list.append(row)
    return key_list


def tabulate_keys(gpg, explain=False):
    """
    List all keys in a table for printing on the CLI.

    Will print a nice table of keys with Name, Comment, E-mail, Expires and Fingerprint.
    If explain = Truem, it will exit with returncode 1 when no keys are present.

    :param gpg: GPG objects
    :param explain: With explain is True, more text is added and will exit(1) when no keys are present.
    :return: None.
    """
    result = gpg.list_keys(secret=True)
    if len(result):
        from tabulate import tabulate
        print(tabulate(list_keys(gpg=gpg), headers=("Name", "Comment", "E-mail", "Expires", "Fingerprint")))
    else:
        echo_info("No keys found in KECPKG keyring. Use `--import-key` or `--create-key` to add a "
                  "secret key to the KECPKG keyring in order to sign KECPKG's.")
        if explain:
            sys.exit(1)


def parse_key_uids(uids):
    """
    Parse GPG key uids into a dictionary with Name, Comment and email.

    If the uids is a listof a (single) uids, the uids will be unpacked from the list.
    example uids: `['KE-works BV (KECPKG SIGAUTH TEST KEY) <hostmaster@ke-works.com>']`

    :param uids: the uids string of a GPG key.
    :return: dict with the keys: {name=..., comment=..., email=...}
    """
    uids_pattern = r"(?P<name>.+) \((?P<comment>.+)\)( <(?P<email>.+)>)?"
    if isinstance(uids, list) and len(uids) == 1:
        uids = uids[0]

    match = re.match(uids_pattern, uids)

    return match.groupdict()
