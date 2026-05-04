import json
import os
from zipfile import ZipFile

from click.testing import CliRunner

from kecpkg.cli import kecpkg
from kecpkg.commands.build import generate_artifact_hashes
from kecpkg.settings import copy_default_settings, save_settings
from kecpkg.utils import ensure_dir_exists, get_package_dir
from tests.utils import BaseTestCase, temp_chdir, touch_file


class TestBuildWithoutMarkerFile(BaseTestCase):
    """Regression tests for the silent-None bug in :func:`get_package_dir`.

    When the current working directory contains neither a ``.kecpkg_settings.json``
    nor a ``package_info.json`` marker, :func:`get_package_dir` used to return
    ``None`` silently when no positional ``package_name`` was supplied. Downstream
    callers such as ``kecpkg build`` then crashed with::

        TypeError: expected str, bytes or os.PathLike object, not NoneType

    These tests pin the behaviour: with ``fail=True`` (the default) the helper
    must exit loudly with a descriptive error, regardless of whether a
    ``package_name`` was given.
    """

    def test_get_package_dir_fails_loud_without_marker_and_no_name(self):
        from kecpkg.utils import get_package_dir as _get

        with temp_chdir():
            with self.assertRaises(SystemExit) as cm:
                _get(package_name=None, fail=True)
            self.assertEqual(cm.exception.code, 1)

    def test_get_package_dir_returns_none_when_fail_false(self):
        """``fail=False`` callers (e.g. ``get_package_name``) keep the soft return."""
        from kecpkg.utils import get_package_dir as _get

        with temp_chdir():
            self.assertIsNone(_get(package_name=None, fail=False))
            self.assertIsNone(_get(package_name="does-not-exist", fail=False))

    def test_build_command_without_marker_fails_cleanly(self):
        """``kecpkg build --settings ...`` from a dir without a marker file must
        not crash with ``TypeError``; it should exit non-zero with a clear message.
        """
        with temp_chdir():
            settings_path = "alt-settings.json"
            with open(settings_path, "w") as fh:
                json.dump(copy_default_settings(), fh)

            runner = CliRunner()
            result = runner.invoke(kecpkg, ["build", "--settings", settings_path])

            self.assertNotEqual(
                result.exit_code,
                0,
                "Expected build to fail without a marker file in cwd; output:\n{}".format(
                    result.output
                ),
            )
            self.assertNotIsInstance(
                result.exception,
                TypeError,
                "build crashed with TypeError instead of failing cleanly:\n{}".format(
                    result.output
                ),
            )


class TestCommandPurge(BaseTestCase):
    def test_build_non_interactive(self):
        pkgname = "new_pkg"

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["build", pkgname])
            self.assertEqual(
                result.exit_code,
                0,
                "Results of the run were: \n---\n{}\n---".format(result.output),
            )
            self.assertExists(os.path.join(package_dir, "dist"))

            # check if dist is filled
            package_dir_contents = os.listdir(os.path.join(package_dir, "dist"))
            self.assertTrue(len(package_dir_contents), 1)

    def test_build_with_prune(self):
        pkgname = "new_pkg"

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["build", pkgname])
            self.assertEqual(
                result.exit_code,
                0,
                "Results of the run were: \n---\n{}\n---".format(result.output),
            )
            self.assertExists(os.path.join(package_dir, "dist"))

            # check if dist is filled
            package_dir_contents = os.listdir(os.path.join(package_dir, "dist"))
            self.assertTrue(len(package_dir_contents), 1)

            # restart the build, with prune and check if dist still has 1
            result = runner.invoke(kecpkg, ["build", pkgname, "--prune"])
            self.assertEqual(
                result.exit_code,
                0,
                "Results of the run were: \n---\n{}\n---".format(result.output),
            )
            self.assertExists(os.path.join(package_dir, "dist"))

            # check if dist is filled
            package_dir_contents = os.listdir(os.path.join(package_dir, "dist"))
            self.assertTrue(len(package_dir_contents), 1)

    def test_build_with_extra_ignores(self):
        pkgname = "new_pkg"

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))
            ensure_dir_exists(os.path.join(package_dir, "data"))

            # add additional files (to exclude for building later)
            touch_file(os.path.join(package_dir, "data", "somefile.txt"))
            touch_file(os.path.join(package_dir, "local_extra_file.someext.txt"))

            os.chdir(package_dir)

            # check if those files exists
            package_dir_contents = os.listdir(os.path.join(package_dir))
            self.assertTrue("local_extra_file.someext.txt" in package_dir_contents)
            self.assertTrue("data" in package_dir_contents)

            # set exclude_paths in settings
            settings = copy_default_settings()
            settings["exclude_paths"] = ["data", "local_extra_file.*"]
            save_settings(settings, package_dir=package_dir)

            # run the builder
            result = runner.invoke(kecpkg, ["build", pkgname, "--verbose"])
            self.assertEqual(
                result.exit_code,
                0,
                "Results of the run were: \n---\n{}\n---".format(result.output),
            )
            self.assertExists(os.path.join(package_dir, "dist"))

            # check the zip such that the extra files are not packaged
            dist_list = os.listdir(os.path.join(package_dir, "dist"))
            zipfile = ZipFile(os.path.join(package_dir, "dist", dist_list[0]), "r")
            contents = zipfile.namelist()

            self.assertFalse("local_extra_file.someext.txt" in contents)
            self.assertFalse("data" in contents)

    def test_build_with_alternate_config(self):
        pkgname = "new_pkg"
        alt_settings = "alt-settings.json"

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            # set alternative settings path
            settings = copy_default_settings()
            settings["package_name"] = pkgname
            save_settings(
                settings, package_dir=package_dir, settings_filename=alt_settings
            )

            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["build", pkgname, "--config", alt_settings])
            self.assertEqual(
                result.exit_code,
                0,
                "Results of the run were: \n---\n{}\n---".format(result.output),
            )
            self.assertExists(os.path.join(package_dir, "dist"))

            dist_dir_contents = os.listdir(os.path.join(package_dir, "dist"))
            self.assertTrue(len(dist_dir_contents), 1)
            self.assertTrue(
                pkgname in dist_dir_contents[0],
                "the name of the pkg `{}` should be in the name of "
                "the built kecpkg `{}`".format(pkgname, dist_dir_contents[0]),
            )

    def test_build_with_no_update_package_info(self):
        pkgname = "new_pkg"
        with temp_chdir():
            runner = CliRunner()
            runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ["build", pkgname, "--no-update"])
            self.assertEqual(
                result.exit_code,
                0,
                "build --no-update failed:\n{}".format(result.output),
            )
            self.assertExists(os.path.join(package_dir, "dist"))


class TestGenerateArtifactHashes(BaseTestCase):
    def test_bad_algorithm_raises(self):
        import tempfile as _tempfile

        with _tempfile.TemporaryDirectory() as d:
            settings = copy_default_settings()
            settings["hash_algorithm"] = "not_a_real_algorithm"
            with self.assertRaises(Exception):
                generate_artifact_hashes(d, set(), settings)
