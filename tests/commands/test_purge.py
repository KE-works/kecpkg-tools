import os

from click.testing import CliRunner

from kecpkg.cli import kecpkg
from kecpkg.utils import get_package_dir
from tests.utils import temp_chdir, BaseTestCase


class TestCommandPurge(BaseTestCase):
    def test_purge_non_interactive(self):
        pkgname = 'new_pkg'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--no-venv'])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            result = runner.invoke(kecpkg, ['purge', pkgname, '--force'])
            self.assertFalse(os.path.exists(package_dir))


