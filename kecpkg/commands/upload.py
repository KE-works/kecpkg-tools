import os
import sys

import click as click
import requests
from pykechain import Client, get_project
from requests.compat import urljoin

from kecpkg.commands.utils import CONTEXT_SETTINGS, echo_info, echo_success, echo_failure
from kecpkg.settings import load_settings, save_settings
from kecpkg.utils import get_package_dir, get_package_name


@click.command(context_settings=CONTEXT_SETTINGS,
               short_help="Upload package to a KE-chain 2 scope")
@click.argument('package', required=False)
@click.option('--url', '-U', help="URL of the KE-chain instance (eg. https://<instance>.ke-chain.com)")
@click.option('--username', '-u', help="username for KE-chain", default=os.environ.get('USER', ''))
@click.option('--password', '-p', help="password for KE-chain")
@click.option('--token', help="token for KE-chain access")
@click.option('--scope', help="scope name to upload the kecpkg to")
@click.option('--scope-id', help="UUID of the scope to upload the kecpkg to", type=click.UUID)
@click.option('--service-id', help="(optional) id of the service to reupload", type=click.UUID)
@click.option('--reupload', '--replace', '-r', is_flag=True, default=False,
              help="(optional) reupload the kecpkg to an already existing service")
@click.option('--interactive', '-i', is_flag=True, help="interactive mode; guide me through the upload")
@click.option('--kecpkg', help="(optional) path to the kecpkg file to upload", type=click.File)
@click.option('--store/--no-store', is_flag=True, default=True,
              help="(optional) flag to store provided interactive information to settings (except pass)")
def upload(package=None, url=None, username=None, password=None, token=None, scope=None, scope_id=None, kecpkg=None,
           **options):
    """
    Upload built kecpkg to KE-chain.

    If no options are provided, the interactive mode is triggered.
    """
    package_name = package or get_package_name() or click.prompt('Package name')
    settings = load_settings(package_dir=get_package_dir(package_name))

    if not url or not (username and password) or not (token) or not (scope or scope_id) or options.get('interactive'):
        url = click.prompt('Url (incl http(s)://)', default=settings.get('url') or url)
        username = click.prompt('Username', default=settings.get('username') or username)
        password = click.prompt('Password', hide_input=True)

        client = Client(url)
        client.login(username=username, password=password)
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

        if options.get('reupload') and options.get('service_id') or settings.get('service_id'):
            scope = client.scope(scope_id)

    # store to settings
    if options.get('store'):
        settings.update(dict(
            url=url,
            username=username,
            scope_id=str(scope_id)
        ))
        save_settings(settings)

    # do upload
    build_path = os.path.join(get_package_dir(package_name), settings.get('build_dir'))
    if not build_path:
        echo_failure('Cannot find build path, please do build kecpkg first')
        sys.exit(400)
    scope_to_upload = get_project(url, username, password, token, scope_id=scope_id)
    upload_package(scope_to_upload, build_path, kecpkg, settings)


def upload_package(scope, build_path=None, kecpkg_path=None, settings=None):
    """
    Upload the package from build_path to the right scope, create a new KE-chain SIM service.

    :param scope: scope object (pykechain)
    :param build_path: path to the build directory in which the to-be uploaded script resides
    :param kecpkg_path: path to the kecpkg file to upload (no need to provide build_path)
    :param settings: settings of the package
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

    # Create new service in KE-chain
    payload = dict(
        name=settings.get('package_name'),
        description=settings.get('description', ''),
        script_version=settings.get('version', ''),
        script_type='PYTHON SCRIPT',
        env_version=settings.get('python_version'),
        id='',
        scope=scope.id
    )

    create_uri = '/api/services.json'
    r = scope._client._request('POST', urljoin(scope._client.api_root, create_uri), data=payload)
    if r.status_code != requests.codes.created:
        echo_failure('Unexpected response from the server: {}'.format((r, r.text)))
        sys.exit(r.status_code)
    response = r.json()
    new_service = response.get('results')[0]

    # Upload as attachment to new service in KE-chain
    r = scope._client._request('POST', "{}/{}".format(new_service.get('url'), 'upload.json'),
                               files={'attachment': (os.path.basename(kecpkg_path), open(kecpkg_path, 'rb'))})

    if r.status_code != requests.codes.accepted:
        echo_failure('Unexpected response from the server: {}'.format((r, r.text)))
        sys.exit(r.status_code)

    # Wrap up party!
    echo_success("kecpkg `{}` successfully uploaded to KE-chain.".format(os.path.basename(kecpkg_path)))
    success_url = "{api_root}/#scopes/{scope_id}/scripts/{script_id}".format(
        api_root=scope._client.api_root,
        scope_id=scope.id,
        script_id=new_service.get('id')
    )
    echo_success("To view the newly created service, go to: `{}`".format(success_url))

    # update settings
    settings['service_id'] = str(new_service.id)
    from datetime import datetime
    settings['last_upload'] = datetime.isoformat()
    save_settings(settings)


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
