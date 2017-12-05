import os

from click.testing import CliRunner

from kecpkg.cli import kecpkg
from tests.utils import temp_chdir, BaseTestCase


class TestCommandNew(BaseTestCase):
    def test_new_non_interactive_no_venv(self):
        pkgname = 'new_pkg'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--no-venv'])

            self.assertEqual(result.exit_code, 0)

            self.assertTrue(os.path.exists(os.path.join(d, pkgname)))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, 'script.py')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, 'package_info.json')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, 'README.md')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, 'requirements.txt')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, '.gitignore')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, '.kecpkg_settings.json')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, '.idea')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, '.env')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, '.idea', 'runConfigurations')))
            self.assertTrue(
                os.path.exists(os.path.join(d, pkgname, '.idea', 'runConfigurations', 'Build_the_kecpkg.xml')))
            self.assertTrue(
                os.path.exists(os.path.join(d, pkgname, '.idea', 'runConfigurations', 'Upload_the_kecpkg.xml')))

            self.assertFalse(os.path.exists(os.path.join(d, pkgname, 'venv')))

    def test_new_non_interactive_with_venv(self):
        pkgname = 'new_pkg'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname])

            e = result.exception

            self.assertEqual(result.exit_code, 0)

            self.assertTrue(os.path.exists(os.path.join(d, pkgname, 'venv')))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, 'venv', 'bin', 'activate')))

    def test_new_non_iteractive_with_alternate_script(self):
        pkgname = 'new_pkg'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--script', 'foobar', '--no-venv'])

            self.assertEqual(result.exit_code, 0)

            self.assertTrue(os.path.exists(os.path.join(d, pkgname, 'foobar.py')))

    def test_new_non_interactive_with_alternate_venv_name(self):
        pkgname = 'new_pkg'
        venv_name = '_v'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--venv', venv_name])

            self.assertEqual(result.exit_code, 0)

            self.assertTrue(os.path.exists(os.path.join(d, pkgname, venv_name)))
            self.assertTrue(os.path.exists(os.path.join(d, pkgname, venv_name, 'bin', 'activate')))
