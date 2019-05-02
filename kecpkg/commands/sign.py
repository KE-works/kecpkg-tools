import os
import sys

import click

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.gpg import get_gpg, list_keys
from kecpkg.settings import SETTINGS_FILENAME, GNUPG_KECPKG_HOME
from kecpkg.utils import remove_path, echo_info, echo_success, echo_failure


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Perform package signing and key management.")
@click.argument('package', required=False)
@click.option('--settings', '--config', '-s', 'settings_filename',
              help="path to the setting file (default `{}`".format(SETTINGS_FILENAME),
              type=click.Path(), default=SETTINGS_FILENAME)
@click.option('--keyid', '--key-id', '-k', 'sign_keyid',
              help="ID (name, email, KeyID) of the cryptographic key to do the sign the contents of the package. "
                   "Use in combination with `--sign`")
@click.option('--passphrase', '-p', 'sign_passphrase', hide_input=True,
              help="Passphrase of the cryptographic key to sign the contents of the package. "
                   "Use in combination with `--sign` and `--keyid`")
@click.option('--add-key', '--addkey', '-a', 'add_key_file', type=click.Path(exists=True),
              help="Add keyfile (in .asc) to the KECPKG keyring which will be used for signing")
@click.option('--delete-key', '--deletekey', 'do_delete_key',
              help="Delete key by its fingerprint permanently from the KECPKG keyring. To retrieve the full "
                   "fingerprint of the key, use the `--list` option and look at the 'fingerprint' section.")
@click.option('--clear', 'do_clear', is_flag=True, default=False,
              help="Clear all keys from the KECPKG keyring")
@click.option('--list', '-l', 'do_list', is_flag=True,
              help="List all available keys in the KECPKG keyring")
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def sign(package=None, **options):
    """Sign the package."""

    # echo_info('Locating package ``'.format(package))
    # package_dir = get_package_dir(package_name=package)
    # package_name = os.path.basename(package_dir)
    # echo_info('Package `{}` has been selected'.format(package_name))
    # settings = load_settings(package_dir=package_dir, settings_filename=options.get('settings_filename'))

    # first subcommands that do not require package to be selected.

    def _do_clear():
        echo_info("Clearing all keys from the KECPKG keyring")
        remove_path(GNUPG_KECPKG_HOME)
        echo_success("Completed")
        sys.exit(0)

    def _do_list(gpg):
        result = gpg.list_keys(secret=True)
        if len(result):
            from tabulate import tabulate
            print(tabulate(list_keys(gpg=gpg), headers=("Name", "Comment", "E-mail", "Expires", "Fingerprint")))
        else:
            echo_info("No keys found in KECPKG keyring. Use `--add-key` to add a private key to the KECPKG keyring.")
            sys.exit(1)
        sys.exit(0)

    def _add_key_file(gpg, options):
        echo_info("Importing secret key into KECPKG keyring from '{}'".format(options.get('add_key_file')))
        result = gpg.import_keys(open(os.path.abspath(options.get('add_key_file')), 'rb').read())
        # pprint(result.__dict__)
        if result and result.sec_imported:
            echo_success("Succesfully imported secret key into the KECPKG keystore")
            _do_list(gpg=gpg)
            sys.exit(0)
        elif result and result.unchanged:
            echo_failure("Did not import the secret key into the KECPKG keystore. The key was already "
                         "in place and was unchanged")
            _do_list(gpg=gpg)
            sys.exit(1)
        echo_failure("Did not import a secret key into the KECPKG keystore. Is something wrong "
                     "with the file: '{}'? Are you sure it is a ASCII file containing a "
                     "private key block?".format(options.get('add_key_file')))
        sys.exit(1)

    def _do_delete_key(gpg, options):
        echo_info("Deleting private key with ID '{}' from the KECPKG keyring".format(options.get('do_delete_key')))

        # custom call to gpg using --delete-secret-and-public-key
        result = gpg.result_map['delete'](gpg)
        p = gpg._open_subprocess(['--yes', '--delete-secret-and-public-key', options.get('do_delete_key')])
        gpg._collect_output(p, result, stdin=p.stdin)

        # result = gpg.delete_keys(fingerprints=options.get('do_delete_key'),
        #                          secret=True,
        #                          passphrase=options.get('sign_passphrase'))
        # pprint(result.__dict__)
        if result and result.stderr.find("failed") < 0:
            echo_success("Succesfully deleted key")
            _do_list(gpg=gpg)
            sys.exit(0)
        sys.exit(1)

    if options.get('do_clear'):
        _do_clear()

    if options.get('do_list'):
        echo_info("Listing all keys from the KECPKG keyring")
        _do_list(gpg=get_gpg())

    if options.get('add_key_file'):
        _add_key_file(gpg=get_gpg(), options=options)

    if options.get('do_delete_key'):
        _do_delete_key(gpg=get_gpg(), options=options)
