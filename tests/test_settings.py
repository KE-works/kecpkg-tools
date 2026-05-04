import json
import os
import tempfile

from tests.utils import BaseTestCase, temp_chdir


class TestCopyDefaultSettings(BaseTestCase):
    def test_returns_independent_copy(self):
        from kecpkg.settings import copy_default_settings

        s1 = copy_default_settings()
        s2 = copy_default_settings()
        s1["version"] = "99.0"
        self.assertNotEqual(s1["version"], s2["version"])

    def test_has_expected_keys(self):
        from kecpkg.settings import copy_default_settings

        s = copy_default_settings()
        for key in ("version", "pyversions", "python_version", "build_dir"):
            self.assertIn(key, s)

    def test_pyversions_are_current(self):
        from kecpkg.settings import copy_default_settings

        s = copy_default_settings()
        self.assertIn("3.12", s["pyversions"])
        self.assertIn("3.14", s["pyversions"])
        for deprecated in ("3.7", "3.8", "3.9"):
            self.assertNotIn(deprecated, s["pyversions"])


class TestGetSettingsFilepath(BaseTestCase):
    def test_default_returns_cwd_based_path(self):
        from kecpkg.settings import get_settings_filepath, SETTINGS_FILENAME

        result = get_settings_filepath()
        self.assertTrue(result.endswith(SETTINGS_FILENAME))

    def test_with_package_dir(self):
        from kecpkg.settings import get_settings_filepath, SETTINGS_FILENAME

        result = get_settings_filepath(package_dir="/some/dir")
        self.assertEqual(result, os.path.join("/some/dir", SETTINGS_FILENAME))

    def test_custom_settings_filename(self):
        from kecpkg.settings import get_settings_filepath

        result = get_settings_filepath(package_dir="/some/dir", settings_filename="custom.json")
        self.assertEqual(result, "/some/dir/custom.json")

    def test_none_settings_filename_falls_back_to_default(self):
        from kecpkg.settings import get_settings_filepath, SETTINGS_FILENAME

        result = get_settings_filepath(package_dir="/some/dir", settings_filename=None)
        self.assertEqual(result, os.path.join("/some/dir", SETTINGS_FILENAME))


class TestLoadSettings(BaseTestCase):
    def test_load_existing_settings(self):
        from kecpkg.settings import load_settings, save_settings, copy_default_settings

        with tempfile.TemporaryDirectory() as d:
            settings = copy_default_settings()
            settings["package_name"] = "testpkg"
            save_settings(settings, package_dir=d)

            loaded = load_settings(package_dir=d)
            self.assertEqual(loaded["package_name"], "testpkg")

    def test_load_missing_settings_exits(self):
        from kecpkg.settings import load_settings

        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(SystemExit) as cm:
                load_settings(package_dir=d)
            self.assertEqual(cm.exception.code, 404)

    def test_lazy_load_returns_empty_dict_when_missing(self):
        from kecpkg.settings import load_settings

        with tempfile.TemporaryDirectory() as d:
            result = load_settings(package_dir=d, lazy=True)
            self.assertEqual(result, {})


class TestSaveSettings(BaseTestCase):
    def test_save_and_reload(self):
        from kecpkg.settings import save_settings, load_settings, copy_default_settings

        with tempfile.TemporaryDirectory() as d:
            settings = copy_default_settings()
            settings["version"] = "1.2.3"
            save_settings(settings, package_dir=d)

            reloaded = load_settings(package_dir=d)
            self.assertEqual(reloaded["version"], "1.2.3")

    def test_save_is_atomic_on_overwrite(self):
        from kecpkg.settings import save_settings, load_settings, copy_default_settings

        with tempfile.TemporaryDirectory() as d:
            s1 = copy_default_settings()
            s1["version"] = "1.0.0"
            save_settings(s1, package_dir=d)

            s2 = copy_default_settings()
            s2["version"] = "2.0.0"
            save_settings(s2, package_dir=d)

            reloaded = load_settings(package_dir=d)
            self.assertEqual(reloaded["version"], "2.0.0")


class TestRestoreSettings(BaseTestCase):
    def test_restore_creates_defaults(self):
        from kecpkg.settings import restore_settings, load_settings, DEFAULT_SETTINGS

        with tempfile.TemporaryDirectory() as d:
            restore_settings(package_dir=d)
            loaded = load_settings(package_dir=d)
            self.assertEqual(loaded["python_version"], DEFAULT_SETTINGS["python_version"])
