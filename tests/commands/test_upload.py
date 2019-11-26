import os
from unittest import skipIf

from click.testing import CliRunner
from envparse import Env

from kecpkg.cli import kecpkg
from kecpkg.utils import get_package_dir
from tests.utils import temp_chdir, BaseTestCase, running_on_ci


@skipIf(running_on_ci(), reason="Test do not work on a CI environment")
@skipIf("os.getenv('KECHAIN_URL') is None",
        reason="Skipping test as the KECHAIN_URL is not available as environment variable. Cannot upload kecpkg to "
               "test this functionality. Provice a `.env` file locally to enable these tests.")
class TestCommandUpload(BaseTestCase):
    def test_upload_non_interactive(self):
        pkgname = 'new_pkg'
        env = Env.read_envfile()

        self.assertTrue(os.environ.get('KECHAIN_URL'),
                        "KECHAIN_URL is not set in environment, cannot perform this test")

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--no-venv'])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ['build', pkgname])
            self.assertEqual(result.exit_code, 0)
            self.assertExists(os.path.join(package_dir, 'dist'))
            pkgpath = os.path.join(package_dir, 'dist', '{}-0.0.1-py3.5.kecpkg'.format(pkgname))
            self.assertExists(pkgpath)

            result = runner.invoke(kecpkg, [
                'upload', pkgname,
                '--url', os.environ.get('KECHAIN_URL'),
                '--token', os.environ.get('KECHAIN_TOKEN'),
                '--scope-id', os.environ.get('KECHAIN_SCOPE_ID'),
                '--kecpkg', pkgpath,
                '--store'  # store the service_id in the settings (for teardown)
            ])
            self.assertEqual(result.exit_code, 0)

            # teardown the just uploaded service
            from kecpkg.settings import load_settings
            settings = load_settings(package_dir=get_package_dir(pkgname))

            from pykechain import get_project
            scope = get_project(
                url=os.environ.get('KECHAIN_URL'),
                token=os.environ.get('KECHAIN_TOKEN'),
                scope_id=os.environ.get('KECHAIN_SCOPE_ID')
            )
            service = scope.service(pk=settings.get('service_id'))
            service.delete()
