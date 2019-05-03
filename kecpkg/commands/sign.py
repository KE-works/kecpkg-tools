import os
import sys
from pprint import pprint

import click

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.gpg import get_gpg, list_keys
from kecpkg.settings import SETTINGS_FILENAME, GNUPG_KECPKG_HOME, load_settings, DEFAULT_SETTINGS
from kecpkg.utils import remove_path, echo_info, echo_success, echo_failure, get_package_dir




@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Perform package signing and key management.")
@click.argument('package', required=False)
@click.option('--settings', '--config', '-s', 'settings_filename',
              help="path to the setting file (default `{}`".format(SETTINGS_FILENAME),
              type=click.Path(), default=SETTINGS_FILENAME)
@click.option('--keyid', '--key-id', '-k', 'keyid',
              help="ID (name, email, KeyID) of the cryptographic key to do the operation with. ")
# @click.option('--passphrase', '-p', 'sign_passphrase', hide_input=True,
#               help="Passphrase of the cryptographic key to sign the contents of the package. "
#                    "Use in combination with `--sign` and `--keyid`")
@click.option('--import-key', '--import', '-i', 'do_import', type=click.Path(exists=True),
              help="Import secret keyfile (in .asc) to the KECPKG keyring which will be used for signing. "
                   "You can export a created key in gpg with `gpg -a --export-secret-key [keyID] > secret_key.asc`.")
@click.option('--delete-key', '-d', 'do_delete_key',
              help="Delete key by its fingerprint permanently from the KECPKG keyring. To retrieve the full "
                   "fingerprint of the key, use the `--list` option and look at the 'fingerprint' section.")
@click.option('--create-key', '-c', 'do_create_key', is_flag=True,
              help="Create secret key and add it to the KECPKG keyring.")
@click.option('--export-key', '--export','-e', 'do_export_key', type=click.Path(), default="pub_key.asc",
              help="Export public key to filename with `--keyid KeyID` in .ASC format for public distribution.")
@click.option('--clear-keyring', 'do_clear', is_flag=True, default=False,
              help="Clear all keys from the KECPKG keyring")
@click.option('--list', '-l', 'do_list', is_flag=True,
              help="List all available keys in the KECPKG keyring")
@click.option('--yes', '-y', 'do_yes', is_flag=True,
              help="Don't ask questions, just do it.")
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def sign(package=None, **options):
    """Sign the package."""

    # echo_info('Locating package ``'.format(package))
    # package_dir = get_package_dir(package_name=package)
    # package_name = os.path.basename(package_dir)
    # echo_info('Package `{}` has been selected'.format(package_name))
    # settings = load_settings(package_dir=package_dir, settings_filename=options.get('settings_filename'))

    # first subcommands that do not require package to be selected.

    def _do_clear(options):
        echo_info("Clearing all keys from the KECPKG keyring")
        if not options.get('do_yes'):
            options['do_yes'] = click.confirm("Are you sure you want to clear the KECPKG keyring?", default=False)
        if options.get('do_yes'):
            remove_path(GNUPG_KECPKG_HOME)
            echo_success("Completed")
            sys.exit(0)
        else:
            echo_failure("Not removing the KECPKG keyring")
            sys.exit(1)

    def _do_list(gpg, explain=False):
        if explain: echo_info("Listing all keys from the KECPKG keyring")
        result = gpg.list_keys(secret=True)
        if len(result):
            from tabulate import tabulate
            print(tabulate(list_keys(gpg=gpg), headers=("Name", "Comment", "E-mail", "Expires", "Fingerprint")))
        else:
            if explain:
                echo_info("No keys found in KECPKG keyring. Use `--import-key` or `--create-key` to add a "
                          "secret key to the KECPKG keyring in order to sign KECPKG's.")
                sys.exit(1)

    def _do_import(gpg, options):
        echo_info("Importing secret key into KECPKG keyring from '{}'".format(options.get('do_import')))
        result = gpg.import_keys(open(os.path.abspath(options.get('do_import')), 'rb').read())
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
                     "private key block?".format(options.get('do_import')))
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

        echo_failure("Could not delete key.")
        sys.exit(1)

    def _do_create_key(gpg, options):
        echo_info("Will create a secret key and store it into the KECPKG keyring.")
        package_dir = get_package_dir(package_name=package, fail=False)
        settings = DEFAULT_SETTINGS
        if package_dir is not None:
            package_name = os.path.basename(package_dir)
            echo_info('Package `{}` has been selected'.format(package_name))
            settings = load_settings(package_dir=package_dir, settings_filename=options.get('settings_filename'))

        key_info = {'name_real': click.prompt("Name", default=settings.get('name')),
                    'name_comment': click.prompt("Comment", default="KECPKG SIGNING KEY"),
                    'name_email': click.prompt("Email", default=settings.get('email')),
                    'expire_date': click.prompt("Expiration in months", default=12,
                                                value_proc=lambda i: "{}m".format(i)), 'key_type': 'RSA',
                    'key_length': 4096,
                    'key_usage': '',
                    'subkey_type': 'RSA',
                    'subkey_length': 4096,
                    'subkey_usage': 'encrypt,sign,auth',
                    'passphrase': ''}

        passphrase = click.prompt("Passphrase", hide_input=True)
        passphrase_confirmed = click.prompt("Confirm passphrase", hide_input=True)
        if passphrase == passphrase_confirmed:
            key_info['passphrase'] = passphrase
        else:
            raise ValueError("The passphrases did not match.")

        echo_info("Creating the secret key '{name_real} ({name_comment}) <{name_email}>'".format(**key_info))
        echo_info("Please move around mouse or generate other activity to introduce sufficient entropy. "
                  "This might take a minute...")
        result = gpg.gen_key(gpg.gen_key_input(**key_info))
        pprint(result.__dict__)
        if result and result.stderr.find('KEY_CREATED'):
            echo_success("The key is succesfully created")
            _do_list(gpg=gpg)
            sys.exit(0)

        echo_failure("Could not generate the key due to an error: '{}'".format(result.stderr))
        sys.exit(1)

    def _do_export_key(gpg, options):
        """Exporting public key"""
        echo_info("Exporting public key")
        if options.get('keyid') is None:
            _do_list(gpg=gpg)
            options['keyid'] = click.prompt("Provide KeyId (name, comment, email, fingerprint) of the key to export")
        result = gpg.export_keys(keyids=[options.get('keyid')], secret=False, armor=True)

        if result is not None:
            with open(options.get('do_export_key'), 'w') as fd:
                fd.write(result)
            echo_success("Sucessfully written public key to '{}'".format(options.get('do_export_key')))
            sys.exit(0)

        echo_failure("Could not export key")
        sys.exit(1)

    if options.get('do_clear'):
        _do_clear(options=options)

    if options.get('do_list'):
        _do_list(gpg=get_gpg(), explain=True)
        sys.exit(0)

    if options.get('do_import'):
        _do_import(gpg=get_gpg(), options=options)

    if options.get('do_delete_key'):
        _do_delete_key(gpg=get_gpg(), options=options)

    if options.get('do_create_key'):
        _do_create_key(gpg=get_gpg(), options=options)

    if options.get('do_export_key'):
        _do_export_key(gpg=get_gpg(), options=options)
