import os

from click.testing import CliRunner

from kecpkg.cli import kecpkg
from kecpkg.commands.config import process_additional_exclude_paths
from kecpkg.settings import copy_default_settings, save_settings
from kecpkg.utils import get_package_dir
from tests.utils import BaseTestCase, temp_chdir


class TestProcessAdditionalExcludePaths(BaseTestCase):
    def test_single_path(self):
        result = process_additional_exclude_paths("data")
        self.assertEqual(result, ["data"])

    def test_multiple_paths_with_spaces(self):
        result = process_additional_exclude_paths("data, input, output")
        self.assertEqual(result, ["data", "input", "output"])

    def test_empty_string(self):
        result = process_additional_exclude_paths("")
        self.assertEqual(result, [""])

    def test_non_string_raises(self):
        with self.assertRaises(AssertionError):
            process_additional_exclude_paths(123)


class TestCommandConfig(BaseTestCase):
    def _make_package(self, runner, pkgname, tmpdir):
        runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
        package_dir = get_package_dir(pkgname)
        self.assertTrue(os.path.exists(package_dir))
        return package_dir

    def test_config_verbose(self):
        pkgname = "cfg_pkg"
        with temp_chdir():
            runner = CliRunner()
            package_dir = self._make_package(runner, pkgname, None)
            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["config", pkgname, "--verbose"])
            self.assertEqual(
                result.exit_code,
                0,
                "config --verbose failed:\n{}".format(result.output),
            )
            self.assertIn("python_version", result.output)

    def test_config_get_existing_key(self):
        pkgname = "cfg_pkg"
        with temp_chdir():
            runner = CliRunner()
            package_dir = self._make_package(runner, pkgname, None)
            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["config", pkgname, "--get", "python_version"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("python_version", result.output)

    def test_config_set_key(self):
        pkgname = "cfg_pkg"
        with temp_chdir():
            runner = CliRunner()
            package_dir = self._make_package(runner, pkgname, None)
            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["config", pkgname, "--set", "version", "9.9.9"])
            self.assertEqual(result.exit_code, 0, result.output)

            # verify it was persisted
            result2 = runner.invoke(kecpkg, ["config", pkgname, "--get", "version"])
            self.assertIn("9.9.9", result2.output)

    def test_config_init_creates_settings(self):
        pkgname = "cfg_pkg"
        with temp_chdir():
            runner = CliRunner()
            package_dir = self._make_package(runner, pkgname, None)
            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["config", pkgname, "--init"], input="n\n")
            self.assertEqual(result.exit_code, 0, result.output)

    def test_config_no_options_shows_success(self):
        pkgname = "cfg_pkg"
        with temp_chdir():
            runner = CliRunner()
            package_dir = self._make_package(runner, pkgname, None)
            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["config", pkgname])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Settings file identified and correct", result.output)
