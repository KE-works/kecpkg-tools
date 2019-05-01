import os
import sys
from pprint import pprint

import click

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.gpg import get_gpg
from kecpkg.settings import SETTINGS_FILENAME, load_settings, GNUPG_KECPKG_HOME
from kecpkg.utils import get_package_dir, remove_path, echo_info, echo_success


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Build the package and create a kecpkg file")
@click.argument('package', required=False)
@click.option('--settings', '--config', '-s', 'settings_filename',
              help="path to the setting file (default `{}`".format(SETTINGS_FILENAME),
              type=click.Path(exists=True), default=SETTINGS_FILENAME)
@click.option('--keyid', '--key-id', '-k', 'sign_keyid',
              help="ID of the cryptographic key to do the sign the contents of the package. "
                   "Use in combination with `--sign`")
@click.option('--passphrase', '-p', 'sign_passphrase', hide_input=True,
              help="Passphrase of the cryptographic key to sing the contents of the package. "
                   "Use in combination with `--sign` and `--keyid`")
@click.option('--addkey', '--add-key', '-a', 'add_key_file', type=click.Path(exists=True),
              help="Add keyfile (in .asc) to the KECPKG keyring which will be used for signing")
@click.option('--clear', 'do_clear', is_flag=True, default=False,
              help="Clear all keys from the KECPKG keyring")
@click.option('--list', '-l', 'do_list', is_flag=True,
              help="List all available keys in the KECPKG keyring")
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def sign(package=None, **options):
    """Sign the package."""
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))
    settings = load_settings(package_dir=package_dir, settings_filename=options.get('settings_filename'))

    if options.get('do_clear'):
        echo_info("Clearing all keys from the KECPKG keyring")
        remove_path(GNUPG_KECPKG_HOME)
        echo_success("Completed")
        sys.exit(0)

    gpg = get_gpg()

    if options.get('do_list'):
        echo_info("Listing all keys from the KECPKG keyring")
        result = gpg.list_keys(secret=False)
        if result:
            pprint(result.__dict__)
            from tabulate import tabulate

            print(tabulate(
                [(r.get('keyid'), r.get('uids'), r.get('fingerprint')) for r in result],
                headers=("KeyID", "Identity", "Fingerprint")
            ))

    if options.get('add_key_file'):
        echo_info("Importing private keys into KECPKG keyring from '{}'".format(options.get('add_key_file')))
        # with open(os.path.abspath(options.get('add_key_file')), 'rb') as fd:
        result = gpg.import_keys(open(os.path.abspath(options.get('add_key_file')), 'rb').read())
        pprint(result.__dict__)
