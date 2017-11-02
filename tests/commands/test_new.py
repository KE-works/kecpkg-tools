import os

from click.testing import CliRunner

from kecpkg.cli import kecpkg
from tests.utils import temp_chdir, BaseTestCase


class TestCommandNew(BaseTestCase):
    def test_new_non_interactive(self):
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
