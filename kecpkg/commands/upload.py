import os
import sys

import click as click
from pykechain import Client, get_project

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.settings import load_settings, save_settings, SETTINGS_FILENAME
from kecpkg.utils import get_package_dir, get_package_name, echo_success, echo_failure, echo_info


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Upload package to a KE-chain 2 scope")
@click.argument('package', required=False)
@click.option('--settings', '--config', '-s', 'settings_filename',
              help="path to the setting file (default `{}`".format(SETTINGS_FILENAME),
              type=click.Path(exists=True), default=SETTINGS_FILENAME)
@click.option('--url', '-U', help="URL of the KE-chain instance (eg. https://<instance>.ke-chain.com)")
@click.option('--username', '-u', help="username for KE-chain", default=os.environ.get('USER', ''))
@click.option('--password', '-p', help="password for KE-chain")
@click.option('--token', help="token for KE-chain access")
@click.option('--scope', help="scope name to upload the kecpkg to")
@click.option('--scope-id', 'scope_id', help="UUID of the scope to upload the kecpkg to", type=click.UUID)
@click.option('--service-id', 'service_id', help="(optional) id of the service to reupload", type=click.UUID)
@click.option('--reupload', '--replace', '-r', is_flag=True, default=False,
              help="(optional) reupload the kecpkg to an already existing service")
@click.option('--interactive', '-i', is_flag=True, help="interactive mode; guide me through the upload")
@click.option('--kecpkg', help="(optional) path to the kecpkg file to upload", type=click.Path())
@click.option('--store/--no-store', is_flag=True, default=True,
              help="(optional) flag to store provided interactive information to settings (except pass)")
def upload(package=None, url=None, username=None, password=None, token=None, scope=None, scope_id=None, kecpkg=None,
           **options):
    """
    Upload built kecpkg to KE-chain.

    If no options are provided, the interactive mode is triggered.
    """
    package_name = package or get_package_name() or click.prompt('Package name')
    settings = load_settings(package_dir=get_package_dir(package_name),
                             settings_filename=options.get('settings_filename'))

    if not url or not ((username and password) or token):
        url = click.prompt('Url (incl http(s)://)', default=settings.get('url') or url)
        username = click.prompt('Username', default=settings.get('username') or username)
        password = click.prompt('Password', hide_input=True)
        # set the interactive world to True for continuation sake
        options['interactive'] = True
    elif not options.get('interactive'):
        url = url or settings.get('url')
        username = username or settings.get('username')
        token = token or settings.get('token')
        scope_id = scope_id or settings.get('scope_id')

    client = Client(url)
    client.login(username=username, password=password, token=token)

    # scope finder
    if not scope_id and settings.get('scope_id') and \
            click.confirm("Do you wish to use the stored `scope_id` in settings: `{}`".format(
                settings.get('scope_id')), default=True):
        scope_id = settings.get('scope_id')

    if not scope_id:
        scopes = client.scopes()
        scope_matcher = [dict(number=i, scope_id=scope.id, scope=scope.name) for i, scope in
                         zip(range(1, len(scopes)), scopes)]

        # nice UI
        echo_info('Choose from following scopes:')
        for match_dict in scope_matcher:
            echo_info("{number} | {scope_id:.8} | {scope}".format(**match_dict))

        scope_match = None
        while not scope_match:
            scope_guess = click.prompt('Row number, part of Id or Scope')
            scope_match = validate_scopes(scope_guess, scope_matcher)

        echo_success("Scope selected: '{scope}' ({scope_id})".format(**scope_match))
        scope_id = scope_match['scope_id']

    scope_to_upload = get_project(url, username, password, token, scope_id=scope_id)

    # service reupload
    service_id = options.get('service_id') or settings.get('service_id')
    if options.get('reupload') and not service_id:
        echo_failure('Please provide a service id to reupload to.')
    elif service_id and not options.get('reupload') and options.get('interactive'):
        if click.confirm("Do you wish to *replace* the previously uploaded service: `{}`".format(service_id),
                         default=True):
            service_id = service_id
        else:
            service_id = None

    # store to settings
    if options.get('store'):
        settings.update(dict(
            url=url,
            username=username,
            scope_id=str(scope_id)
        ))
        if service_id:
            settings['service_id'] = str(service_id)
        save_settings(settings, settings_filename=options.get('settings_filename'))

    # do upload
    build_path = os.path.join(get_package_dir(package_name), settings.get('build_dir'))
    if not os.path.exists(build_path):
        echo_failure('Cannot find build path, please do `kecpkg build` first')
        sys.exit(400)

    upload_package(scope_to_upload, build_path, kecpkg, service_id=service_id, settings=settings,
                   store_settings=options.get('store'), settings_filename=options.get('settings_filename'))


def upload_package(scope, build_path=None, kecpkg_path=None, service_id=None, settings=None, store_settings=True,
                   settings_filename=None):
    """
    Upload the package from build_path to the right scope, create a new KE-chain SIM service.

    :param scope: Scope object (pykechain)
    :param build_path: path to the build directory in which the to-be uploaded script resides
    :param kecpkg_path: path to the kecpkg file to upload (no need to provide build_path)
    :param service_id: UUID of the service to upload to
    :param settings: settings of the package
    :param store_settings: store the settings after update (eg service_id after upload)
    :param settings_filename: pathname of the file where the settings are stored
    :return: None
    """
    # if not (kecpkg_path and not build_path) or not (build_path and not kecpkg_path):
    #     echo_failure("You should provide a build path or a kecpkg path")
    #     sys.exit(404)
    if kecpkg_path and os.path.exists(kecpkg_path):
        kecpkg_path = kecpkg_path
    else:

        built_kecpkgs = os.listdir(build_path)
        if not kecpkg_path and len(built_kecpkgs) > 1 and settings.get('version'):
            built_kecpkgs = [f for f in built_kecpkgs if settings.get('version') in f]
        if not kecpkg_path and len(built_kecpkgs) == 1:
            kecpkg_path = os.path.join(build_path, built_kecpkgs[0])
        else:
            echo_info('Provide correct filename to upload')
            echo_info('\n'.join(os.listdir(build_path)))
            kecpkg_filename = click.prompt('Filename')
            kecpkg_path = os.path.join(build_path, kecpkg_filename)

    if kecpkg_path and os.path.exists(kecpkg_path):
        # ready to upload
        echo_info('Ready to upload `{}`'.format(os.path.basename(kecpkg_path)))
    else:
        echo_failure('Unable to locate kecpkg to upload')
        sys.exit(404)

    # get meta and prepare 2 stage submission
    # 1. fill service information
    # 2. do upload

    if service_id:
        service = scope.service(pk=service_id)
        service.upload(kecpkg_path)
        service.edit(
            name=settings.get('package_name'),
            description=settings.get('description', ''),
            script_version=settings.get('version', '')
        )
    else:
        # Create new service in KE-chain
        service = scope.create_service(
            name=settings.get('package_name'),
            description=settings.get('description', ''),
            version=settings.get('version', ''),
            service_type='PYTHON SCRIPT',
            environment_version=settings.get('python_version'),
            pkg_path=kecpkg_path
        )

    # Wrap up party!
    echo_success("kecpkg `{}` successfully uploaded to KE-chain.".format(os.path.basename(kecpkg_path)))
    # noinspection PyProtectedMember
    success_url = "{api_root}/#scopes/{scope_id}/scripts/{service_id}".format(
        api_root=scope._client.api_root,
        scope_id=scope.id,
        service_id=service.id
    )
    echo_success("To view the newly created service, go to: `{}`".format(success_url))

    # update settings
    if store_settings:
        settings['service_id'] = str(service.id)
        from datetime import datetime
        settings['last_upload'] = str(datetime.now().isoformat())
        save_settings(settings, settings_filename=settings_filename)


def validate_scopes(scope_guess, scope_matcher):
    """Check the scope guess against a set of possible scopes and return correct scope_id."""
    scope_matches = []
    for scope_match in scope_matcher:
        # order is important as '1' can also be in UUID and Name, so we use exclusive if statements
        if scope_guess == str(scope_match['number']):
            scope_matches.append(scope_match)
        elif len(scope_guess) >= 2 and scope_guess.lower() in scope_match['scope_id'].lower():
            scope_matches.append(scope_match)
        elif scope_guess.lower() in scope_match['scope'].lower():
            scope_matches.append(scope_match)

    # only return when a single scope is matched
    if len(scope_matches) == 1:
        return scope_matches[0]
    print('Could not match; be more specific')
    return None
