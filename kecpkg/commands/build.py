import hashlib
import io
import os
from zipfile import ZipFile

import click as click

from kecpkg.commands.utils import CONTEXT_SETTINGS, echo_info
from kecpkg.settings import load_settings, SETTINGS_FILENAME
from kecpkg.utils import ensure_dir_exists, remove_path, get_package_dir, get_artifacts_on_disk, render_package_info, \
    create_file


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
              help="Sign the contents of the package with a cryptographic key. Defaults to not sign.")
@click.option('--keyid', '--key-id', '-k', 'sign_keyid',
              help="ID of the cryptographic key to do the sign the contents of the build package. "
                   "Use in combination with `--sign`")
@click.option('--passphrase', '-p', 'sign_passphrase', prompt=True, hide_input=True,
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

    echo_info('Complete')


def build_package(package_dir, build_path, settings, options=None, verbose=False):
    """Perform the actual building of the kecpkg zip."""
    additional_exclude_paths = settings.get('exclude_paths')

    artifacts = get_artifacts_on_disk(package_dir, verbose=verbose, additional_exclude_paths=additional_exclude_paths)
    dist_filename = '{}-{}-py{}.kecpkg'.format(settings.get('package_name'), settings.get('version'),
                                               settings.get('python_version'))
    echo_info('Creating package name `{}`'.format(dist_filename))

    if verbose: echo_info(("Creating 'ARTIFACTS' file with list of contents and their hashes"))
    generate_artifact_hashes(package_dir, artifacts, settings, verbose=verbose)
    artifacts.append(settings.get('artifacts_filename', 'ARTIFACTS'))

    if options.get('do_sign'):
        sign_package(package_dir, settings, options=options, verbose=verbose)

    with ZipFile(os.path.join(build_path, dist_filename), 'w') as dist_zip:
        for artifact in artifacts:
            dist_zip.write(os.path.join(package_dir, artifact), arcname=artifact)


def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
    """Yield pieces of data from a file-like object until EOF."""
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk


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

    def _hash_of_file(path, algorithm):
        """Return the hash digest of a file."""
        with open(path, 'rb') as archive:
            hash = hashlib.new(algorithm)
            for chunk in read_chunks(archive):
                hash.update(chunk)
        return hash.hexdigest()

    artifacts_fn = settings.get('artifacts_filename', 'ARTIFACTS')
    algorithm = settings.get('hash_algorithm', 'sha256')
    if algorithm not in hashlib.algorithms_guaranteed:
        raise

    artifacts_content = []

    for af in artifacts:
        af_fp = os.path.join(package_dir, af)
        artifacts_content.append('{},{}={},{}\n'.format(
            af,
            algorithm,
            _hash_of_file(af_fp, algorithm=algorithm),
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
    :param verbose: be verbose (or not)
    :return: None
    """
    import logging
    logging.basicConfig(level=logging.DEBUG)

    import gnupg
    logger = logging.getLogger('gnupg')
    gpg = gnupg.GPG()  # binary='/usr/local/bin/gpg')

    echo_info('Signing package contents')

    with open(os.path.join(package_dir, settings.get('artifacts_filename'))) as fp:
        results = gpg.sign_file(fp,
                                keyid=options.get('sign_keyid'),
                                passphrase=options.get('sign_passphrase'),
                                detach=True,
                                output=settings.get('artifacts_filename') + '.SIG')

    if verbose:
        echo_info('Successfully signed the package contents.')
        from pprint import pprint
        pprint(results.__dict__)
