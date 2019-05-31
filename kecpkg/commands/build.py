import hashlib
import os
import sys
from pprint import pprint
from zipfile import ZipFile

import click as click

from kecpkg.commands.sign import verify_signature, verify_artifacts_hashes
from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.gpg import hash_of_file, get_gpg, tabulate_keys
from kecpkg.settings import load_settings, SETTINGS_FILENAME, ARTIFACTS_SIG_FILENAME, ARTIFACTS_FILENAME
from kecpkg.utils import ensure_dir_exists, remove_path, get_package_dir, get_artifacts_on_disk, render_package_info, \
    create_file, echo_success, echo_failure, echo_info


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Build the package and create a kecpkg file")
@click.argument('package', required=False)
@click.option('--settings', '--config', '-s', 'settings_filename',
              help="path to the setting file (default `{}`".format(SETTINGS_FILENAME),
              type=click.Path(exists=True), default=SETTINGS_FILENAME)
@click.option('--clean', '--clear', '--prune', 'clean_first', is_flag=True,
              help='Remove build artifacts before building')
@click.option('--update/--no-update', 'update_package_info', is_flag=True, default=True,
              help="Update the `package-info.json` for the KE-crunch execution to point to correct entrypoint based on "
                   "settings. This is okay to leave ON. Use `--no-update` if you have a custom `package-info.json`.")
@click.option('--sign/--no-sign', 'do_sign', is_flag=True, default=False,
              help="Sign the contents of the package with a cryptographic key from the keyring. Defaults to not sign.")
@click.option('--keyid', '--key-id', '-k', 'sign_keyid',
              help="ID of the cryptographic key to do the sign the contents of the built package. If not provided it "
                   "will use the default key from the KECPKG keystore. Use in combination with `--sign`")
@click.option('--passphrase', '-p', 'sign_passphrase', hide_input=True,
              help="Passphrase of the cryptographic key to sing the contents of the built package. "
                   "Use in combination with `--sign` and `--keyid`")
@click.option('-v', '--verbose', help="Be more verbose", is_flag=True)
def build(package=None, **options):
    """Build the package and create a kecpkg file."""
    echo_info('Locating package ``'.format(package))
    package_dir = get_package_dir(package_name=package)
    package_name = os.path.basename(package_dir)
    echo_info('Package `{}` has been selected'.format(package_name))
    settings = load_settings(package_dir=package_dir, settings_filename=options.get('settings_filename'))

    # ensure build directory is there
    build_dir = settings.get('build_dir', 'dist')
    build_path = os.path.join(package_dir, build_dir)

    if options.get('update_package_info'):
        render_package_info(settings, package_dir=package_dir, backup=True)

    if options.get('clean_first'):
        remove_path(build_path)
    ensure_dir_exists(build_path)

    # do package building
    build_package(package_dir, build_path, settings, options=options, verbose=options.get('verbose'))

    echo_success('Complete')


def build_package(package_dir, build_path, settings, options=None, verbose=False):
    """Perform the actual building of the kecpkg zip."""
    additional_exclude_paths = settings.get('exclude_paths')

    artifacts = get_artifacts_on_disk(package_dir, verbose=verbose,
                                      additional_exclude_paths=additional_exclude_paths)  # type: set
    dist_filename = '{}-{}-py{}.kecpkg'.format(settings.get('package_name'), settings.get('version'),
                                               settings.get('python_version'))
    echo_info('Creating package name `{}`'.format(dist_filename))

    if verbose:
        echo_info("Creating 'ARTIFACTS' file with list of contents and their hashes")
    generate_artifact_hashes(package_dir, artifacts, settings, verbose=verbose)
    artifacts.add(settings.get('artifacts_filename', 'ARTIFACTS'))

    if options.get('do_sign'):
        sign_package(package_dir, settings, options=options, verbose=verbose)
        artifacts.add(settings.get('artifacts_filename', 'ARTIFACTS') + '.SIG')

    with ZipFile(os.path.join(build_path, dist_filename), 'w') as dist_zip:
        for artifact in artifacts:
            dist_zip.write(os.path.join(package_dir, artifact), arcname=artifact)


def generate_artifact_hashes(package_dir, artifacts, settings, verbose=False):
    """
    Generate artifact hashes and store it on disk in a ARTIFACTS file.

    using settings > artifacts_filename to retrieve the artifacts (default ARTIFACTS).
    using settings > hash_algorithm to determine the right algoritm for hashing (default sha256)

    :param package_dir: package directory (fullpath)
    :param artifacts: list of artifacts to store in kecpkg
    :param settings: settings object
    :param verbose: be verbose (or not)
    :return: None
    """
    artifacts_fn = settings.get('artifacts_filename', 'ARTIFACTS')
    algorithm = settings.get('hash_algorithm', 'sha256')
    if algorithm not in hashlib.algorithms_guaranteed:
        raise

    # save content of the artifacts file
    # A line is "README.md,sha256=d831....ccf79a,336"
    #            ^filename ^algo  ^hash          ^size in bytes
    artifacts_content = []

    for af in artifacts:
        # we do not need to create a hash from the ARTIFACTS and ARTIFACTS.SIG file if they are present in the list
        if af not in [artifacts_fn, artifacts_fn + '.SIG']:
            af_fp = os.path.join(package_dir, af)
            artifacts_content.append('{},{}={},{}\n'.format(
                af,
                algorithm,
                hash_of_file(af_fp, algorithm=algorithm),
                os.stat(af_fp).st_size
            ))

    create_file(os.path.join(package_dir, artifacts_fn),
                content=artifacts_content,
                overwrite=True)


def sign_package(package_dir, settings, options=None, verbose=False):
    """
    Sign the package with a GPG/PGP key.

    :param package_dir: directory fullpath of the package
    :param settings: settings object
    :param options: commandline options dictionary passed down.
    :param verbose: be verbose (or not)
    :return: None
    """
    gpg = get_gpg()

    if options.get('sign_keyid') is None:
        tabulate_keys(gpg, explain=True)
        options['sign_keyid'] = click.prompt("Provide Key (Name, Comment, Email, Fingerprint) to sign package with",
                                             default=settings.get('email'))
    if options.get('sign_passphrase') is None:
        options['sign_passphrase'] = click.prompt("Provide Passphrase", hide_input=True)

    echo_info('Signing package contents')

    with open(os.path.join(package_dir, settings.get('artifacts_filename', ARTIFACTS_FILENAME)), 'rb') as fd:
        results = gpg.sign_file(fd,
                                keyid=options.get('sign_keyid'),
                                passphrase=options.get('sign_passphrase'),
                                detach=True,
                                output=settings.get('artifacts_sig_filename', ARTIFACTS_SIG_FILENAME)
                                )
    pprint(results.__dict__)

    if results and results.status is not None:
        echo_info("Signed package contents: {}".format(results.status))
    else:
        failure_text = results.stderr.split("\n")[-2]
        echo_failure("Could not sign the package contents: '{}'".format(failure_text))
        sys.exit(1)

    if verbose:
        echo_success('Successfully signed the package contents.')

    verify_signature(package_dir, ARTIFACTS_FILENAME, ARTIFACTS_SIG_FILENAME)
    verify_artifacts_hashes(package_dir, ARTIFACTS_FILENAME)
