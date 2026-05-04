import os

from click.testing import CliRunner

from kecpkg.cli import kecpkg
from kecpkg.utils import get_package_dir, ensure_dir_exists
from tests.utils import BaseTestCase, temp_chdir


class TestCommandPrune(BaseTestCase):
    def test_prune_with_force_removes_dist(self):
        pkgname = "prune_pkg"
        with temp_chdir():
            runner = CliRunner()
            runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            os.chdir(package_dir)

            runner.invoke(kecpkg, ["build", pkgname])
            self.assertTrue(os.path.exists(os.path.join(package_dir, "dist")))

            result = runner.invoke(kecpkg, ["prune", pkgname, "--force"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertFalse(os.path.exists(os.path.join(package_dir, "dist")))

    def test_prune_with_confirm_yes(self):
        pkgname = "prune_pkg"
        with temp_chdir():
            runner = CliRunner()
            runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            os.chdir(package_dir)

            runner.invoke(kecpkg, ["build", pkgname])
            self.assertTrue(os.path.exists(os.path.join(package_dir, "dist")))

            result = runner.invoke(kecpkg, ["prune", pkgname], input="y\n")
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertFalse(os.path.exists(os.path.join(package_dir, "dist")))

    def test_prune_with_confirm_no(self):
        pkgname = "prune_pkg"
        with temp_chdir():
            runner = CliRunner()
            runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            os.chdir(package_dir)

            runner.invoke(kecpkg, ["build", pkgname])
            self.assertTrue(os.path.exists(os.path.join(package_dir, "dist")))

            result = runner.invoke(kecpkg, ["prune", pkgname], input="n\n")
            self.assertIn("will not be pruned", result.output)
            self.assertTrue(
                os.path.exists(os.path.join(package_dir, "dist")),
                "dist should still exist after declining prune",
            )

    def test_prune_when_no_dist_dir(self):
        pkgname = "prune_pkg"
        with temp_chdir():
            runner = CliRunner()
            runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["prune", pkgname, "--force"])
            self.assertIn("does not exist", result.output)
