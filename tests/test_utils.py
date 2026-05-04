import io
import os
import tempfile

from tests.utils import BaseTestCase, temp_chdir


class TestEnsureDirExists(BaseTestCase):
    def test_creates_missing_directory(self):
        from kecpkg.utils import ensure_dir_exists

        with tempfile.TemporaryDirectory() as d:
            new_dir = os.path.join(d, "subdir")
            self.assertFalse(os.path.exists(new_dir))
            ensure_dir_exists(new_dir)
            self.assertTrue(os.path.exists(new_dir))

    def test_idempotent_on_existing_directory(self):
        from kecpkg.utils import ensure_dir_exists

        with tempfile.TemporaryDirectory() as d:
            ensure_dir_exists(d)
            self.assertTrue(os.path.exists(d))


class TestCreateFile(BaseTestCase):
    def test_creates_file_with_string_content(self):
        from kecpkg.utils import create_file

        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "test.txt")
            create_file(fp, content="hello")
            with open(fp) as f:
                self.assertEqual(f.read(), "hello")

    def test_creates_file_with_list_content(self):
        from kecpkg.utils import create_file

        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "test.txt")
            create_file(fp, content=["line1\n", "line2\n"])
            with open(fp) as f:
                self.assertEqual(f.read(), "line1\nline2\n")

    def test_overwrite_false_raises_on_existing_file(self):
        from kecpkg.utils import create_file

        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "test.txt")
            create_file(fp, content="first")
            with self.assertRaises(SystemExit):
                create_file(fp, content="second", overwrite=False)

    def test_overwrite_true_replaces_content(self):
        from kecpkg.utils import create_file

        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "test.txt")
            create_file(fp, content="first")
            create_file(fp, content="second", overwrite=True)
            with open(fp) as f:
                self.assertEqual(f.read(), "second")


class TestCopyPath(BaseTestCase):
    def test_copy_file(self):
        from kecpkg.utils import copy_path

        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "source.txt")
            dst = os.path.join(d, "dest")
            os.makedirs(dst)
            with open(src, "w") as f:
                f.write("content")
            copy_path(src, dst)
            self.assertTrue(os.path.exists(os.path.join(dst, "source.txt")))

    def test_copy_directory(self):
        from kecpkg.utils import copy_path

        with tempfile.TemporaryDirectory() as d:
            src_dir = os.path.join(d, "mydir")
            os.makedirs(src_dir)
            with open(os.path.join(src_dir, "file.txt"), "w") as f:
                f.write("data")
            dst = os.path.join(d, "dest")
            os.makedirs(dst)
            copy_path(src_dir, dst)
            self.assertTrue(os.path.exists(os.path.join(dst, "mydir", "file.txt")))


class TestRemovePath(BaseTestCase):
    def test_removes_directory(self):
        from kecpkg.utils import remove_path

        with tempfile.TemporaryDirectory() as d:
            target = os.path.join(d, "to_remove")
            os.makedirs(target)
            self.assertTrue(os.path.exists(target))
            remove_path(target)
            self.assertFalse(os.path.exists(target))

    def test_removes_file(self):
        from kecpkg.utils import remove_path

        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, "file.txt")
            with open(fp, "w") as f:
                f.write("x")
            remove_path(fp)
            self.assertFalse(os.path.exists(fp))

    def test_silent_on_nonexistent_path(self):
        from kecpkg.utils import remove_path

        with tempfile.TemporaryDirectory() as d:
            remove_path(os.path.join(d, "ghost"))


class TestBasepath(BaseTestCase):
    def test_returns_basename(self):
        from kecpkg.utils import basepath

        self.assertEqual(basepath("/foo/bar/baz"), "baz")
        self.assertEqual(basepath("/foo/bar/baz/"), "baz")


class TestNormaliseName(BaseTestCase):
    def test_replaces_hyphens(self):
        from kecpkg.utils import normalise_name

        self.assertEqual(normalise_name("my-package"), "my_package")

    def test_replaces_spaces(self):
        from kecpkg.utils import normalise_name

        self.assertEqual(normalise_name("my package"), "my_package")

    def test_lowercases(self):
        from kecpkg.utils import normalise_name

        self.assertEqual(normalise_name("MyPackage"), "mypackage")


class TestGetPackageName(BaseTestCase):
    def test_returns_none_outside_package(self):
        from kecpkg.utils import get_package_name

        with temp_chdir():
            self.assertIsNone(get_package_name())

    def test_returns_name_inside_package(self):
        from kecpkg.utils import get_package_name
        from click.testing import CliRunner
        from kecpkg.cli import kecpkg

        pkgname = "name_test_pkg"
        with temp_chdir():
            runner = CliRunner()
            runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            os.chdir(os.path.join(os.getcwd(), pkgname))
            self.assertEqual(get_package_name(), pkgname)


class TestGetArtifactsOnDisk(BaseTestCase):
    def test_fails_on_missing_root(self):
        from kecpkg.utils import get_artifacts_on_disk

        with self.assertRaises(SystemExit):
            get_artifacts_on_disk("/nonexistent/path/that/does/not/exist")

    def test_returns_files(self):
        from kecpkg.utils import get_artifacts_on_disk

        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "file.txt"), "w") as f:
                f.write("data")
            result = get_artifacts_on_disk(d)
            self.assertIn("file.txt", result)

    def test_verbose_mode(self):
        from kecpkg.utils import get_artifacts_on_disk

        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "file.txt"), "w") as f:
                f.write("data")
            result = get_artifacts_on_disk(d, verbose=True)
            self.assertIn("file.txt", result)

    def test_additional_exclude_paths(self):
        from kecpkg.utils import get_artifacts_on_disk

        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "keep.txt"), "w") as f:
                f.write("keep")
            with open(os.path.join(d, "skip.log"), "w") as f:
                f.write("skip")
            result = get_artifacts_on_disk(d, additional_exclude_paths=["*.log"])
            self.assertIn("keep.txt", result)
            self.assertNotIn("skip.log", result)


class TestReadChunks(BaseTestCase):
    def test_yields_chunks(self):
        from kecpkg.utils import read_chunks

        data = b"hello world"
        chunks = list(read_chunks(io.BytesIO(data), size=5))
        self.assertEqual(chunks, [b"hello", b" worl", b"d"])

    def test_empty_file(self):
        from kecpkg.utils import read_chunks

        chunks = list(read_chunks(io.BytesIO(b"")))
        self.assertEqual(chunks, [])


class TestUnzipPackage(BaseTestCase):
    def test_unzips_to_target(self):
        from kecpkg.utils import unzip_package
        from click.testing import CliRunner
        from kecpkg.cli import kecpkg
        from kecpkg.utils import get_package_dir

        pkgname = "zip_test_pkg"
        with temp_chdir():
            runner = CliRunner()
            runner.invoke(kecpkg, ["new", pkgname, "--no-venv"])
            package_dir = get_package_dir(pkgname)
            os.chdir(package_dir)
            runner.invoke(kecpkg, ["build", pkgname])

            dist_dir = os.path.join(package_dir, "dist")
            kecpkg_file = os.listdir(dist_dir)[0]
            kecpkg_path = os.path.join(dist_dir, kecpkg_file)

            with tempfile.TemporaryDirectory() as out_dir:
                unzip_package(kecpkg_path, out_dir)
                self.assertTrue(len(os.listdir(out_dir)) > 0)
