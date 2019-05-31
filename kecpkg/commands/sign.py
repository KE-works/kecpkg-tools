import os
import sys
from pprint import pprint

import click
from pykechain.utils import temp_chdir

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.gpg import get_gpg, list_keys, hash_of_file
from kecpkg.settings import SETTINGS_FILENAME, GNUPG_KECPKG_HOME, load_settings, DEFAULT_SETTINGS, ARTIFACTS_FILENAME, \
    ARTIFACTS_SIG_FILENAME
from kecpkg.utils import remove_path, echo_info, echo_success, echo_failure, get_package_dir, unzip_package


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
@click.option('--export-key', '--export', '-e', 'do_export_key', type=click.Path(),
              help="Export public key to filename with `--keyid KeyID` in .ASC format for public distribution.")
@click.option('--clear-keyring', 'do_clear', is_flag=True, default=False,
              help="Clear all keys from the KECPKG keyring")
@click.option('--list', '-l', 'do_list', is_flag=True,
              help="List all available keys in the KECPKG keyring")
@click.option('--verify-kecpkg', 'do_verify_kecpkg', type=click.Path(exists=True),
              help="Verify contents and signature of an existing kecpkg.")
@click.option('--yes', '-y', 'do_yes', is_flag=True,
              help="Don't ask questions, just do it.")
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def sign(package=None, **options):
    """Sign the package."""
    # noinspection PyShadowingNames
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
        if explain:
            echo_info("Listing all keys from the KECPKG keyring")
        result = gpg.list_keys(secret=True)
        if len(result):
            from tabulate import tabulate
            print(tabulate(list_keys(gpg=gpg), headers=("Name", "Comment", "E-mail", "Expires", "Fingerprint")))
        else:
            if explain:
                echo_info("No keys found in KECPKG keyring. Use `--import-key` or `--create-key` to add a "
                          "secret key to the KECPKG keyring in order to sign KECPKG's.")
                sys.exit(1)

    # noinspection PyShadowingNames
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

    # noinspection PyShadowingNames
    def _do_delete_key(gpg, options):
        echo_info("Deleting private key with ID '{}' from the KECPKG keyring".format(options.get('do_delete_key')))

        # custom call to gpg using --delete-secret-and-public-key
        result = gpg.result_map['delete'](gpg)
        # noinspection PyProtectedMember
        p = gpg._open_subprocess(['--yes', '--delete-secret-and-public-key', options.get('do_delete_key')])
        # noinspection PyProtectedMember
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

    # noinspection PyShadowingNames
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

    # noinspection PyShadowingNames
    def _do_export_key(gpg, options):
        """Export public key."""
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

    # noinspection PyShadowingNames
    def _do_verify_kecpkg(gpg, options):
        """Verify the kecpkg."""
        echo_info("Verify the contents of the KECPKG and if the KECPKG is signed with a valid signature.")

        current_working_directory = os.getcwd()

        with temp_chdir() as d:
            unzip_package(package_path=os.path.join(current_working_directory, options.get('do_verify_kecpkg')),
                          target_path=d)
            verify_signature(d, artifacts_filename=ARTIFACTS_FILENAME, artifacts_sig_filename=ARTIFACTS_SIG_FILENAME)
            verify_artifacts_hashes(d, artifacts_filename=ARTIFACTS_FILENAME)
        sys.exit(0)

    #
    # Dispatcher to subfunctions
    #

    if options.get('do_clear'):
        _do_clear(options=options)
    elif options.get('do_list'):
        _do_list(gpg=get_gpg(), explain=True)
    elif options.get('do_import'):
        _do_import(gpg=get_gpg(), options=options)
    elif options.get('do_delete_key'):
        _do_delete_key(gpg=get_gpg(), options=options)
    elif options.get('do_create_key'):
        _do_create_key(gpg=get_gpg(), options=options)
    elif options.get('do_export_key'):
        _do_export_key(gpg=get_gpg(), options=options)
    elif options.get('do_verify_kecpkg'):
        _do_verify_kecpkg(gpg=get_gpg(), options=options)
    else:
        sys.exit(500)
    sys.exit(0)


def verify_signature(package_dir, artifacts_filename, artifacts_sig_filename):
    """
    Check signature of the package.

    :param package_dir: directory fullpath of the package
    :param artifacts_filename: path of the artifacts file
    :param artifacts_sig_filename: path of the artifacts signature file
    :return: None
    """
    gpg = get_gpg()
    artifacts_fp = os.path.join(package_dir, artifacts_filename)
    artifacts_sig_fp = os.path.join(package_dir, artifacts_sig_filename)
    if not os.path.exists(artifacts_fp):
        echo_failure("Artifacts file does not exist: '{}'".format(artifacts_filename))
        sys.exit(1)
    if not os.path.exists(artifacts_sig_fp):
        echo_failure("Artifacts signature file does not exist: '{}'. Is the package signed?".
                     format(artifacts_filename))
        sys.exit(1)

    with open(artifacts_sig_fp, 'rb') as sig_fd:
        results = gpg.verify_file(sig_fd, data_filename=artifacts_fp)

    if results.valid:
        echo_info("Verified the signature and the signature is valid")
        echo_info("Signed with: '{}'".format(results.username))
    elif not results.valid:
        echo_failure("Signature of the package is invalid")
        echo_failure(pprint(results.__dict__))
        sys.exit(1)


def verify_artifacts_hashes(package_dir, artifacts_filename):
    """
    Check the hashes of the artifacts in the package.

    :param package_dir: directory fullpath of the package
    :param artifacts_filename: filename of the artifacts file
    :return:
    """
    artifacts_fp = os.path.join(package_dir, artifacts_filename)
    if not os.path.exists(artifacts_fp):
        echo_failure("Artifacts file does not exist: '{}'".format(artifacts_filename))
        sys.exit(1)

    with open(artifacts_fp, 'r') as fd:
        artifacts = fd.readlines()

    # process the file contents
    # A line is "README.md,sha256=d831....ccf79a,336"
    #            ^filename ^algo  ^hash          ^size in bytes
    fails = []
    for af in artifacts:
        # noinspection PyShadowingBuiltins,PyShadowingBuiltins
        filename, hash, orig_size = af.split(',')
        algorithm, orig_hash = hash.split('=')
        fp = os.path.join(package_dir, filename)
        if os.path.exists(fp):
            found_hash = hash_of_file(fp, algorithm)
            found_size = os.stat(fp).st_size
            if found_hash != orig_hash.strip() or found_size != int(orig_size.strip()):
                fails.append("File '{}' is changed in the package.".format(filename))
                fails.append("File '{}' original checksum: '{}', found: '{}'".format(filename, orig_hash, found_hash))
                fails.append("File '{}' original size: {}, found: {}".format(filename, orig_size, found_size))
        else:
            fails.append("File '{}' does not exist".format(filename))

    if fails:
        echo_failure('The package has been changed after building the package.')
        for fail in fails:
            print(fail)
        sys.exit(1)
    else:
        echo_info("Package contents succesfully verified.")
