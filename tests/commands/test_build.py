import os
from zipfile import ZipFile

from click.testing import CliRunner

from kecpkg.cli import kecpkg
from kecpkg.settings import load_settings, save_settings, copy_default_settings
from kecpkg.utils import get_package_dir, ensure_dir_exists
from tests.utils import temp_chdir, BaseTestCase, touch_file


class TestCommandPurge(BaseTestCase):
    def test_build_non_interactive(self):
        pkgname = 'new_pkg'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--no-venv'])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ['build', pkgname])
            self.assertEqual(result.exit_code, 0, "Results of the run were: \n---\n{}\n---".format(result.output))
            self.assertExists(os.path.join(package_dir, 'dist'))


            # check if dist is filled
            package_dir_contents = os.listdir(os.path.join(package_dir, 'dist'))
            self.assertTrue(len(package_dir_contents), 1)

    def test_build_with_prune(self):
        pkgname = 'new_pkg'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--no-venv'])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ['build', pkgname])
            self.assertEqual(result.exit_code, 0, "Results of the run were: \n---\n{}\n---".format(result.output))
            self.assertExists(os.path.join(package_dir, 'dist'))

            # check if dist is filled
            package_dir_contents = os.listdir(os.path.join(package_dir, 'dist'))
            self.assertTrue(len(package_dir_contents), 1)

            # restart the build, with prune and check if dist still has 1
            result = runner.invoke(kecpkg, ['build', pkgname, '--prune'])
            self.assertEqual(result.exit_code, 0, "Results of the run were: \n---\n{}\n---".format(result.output))
            self.assertExists(os.path.join(package_dir, 'dist'))

            # check if dist is filled
            package_dir_contents = os.listdir(os.path.join(package_dir, 'dist'))
            self.assertTrue(len(package_dir_contents), 1)



    def test_build_with_extra_ignores(self):
        pkgname = 'new_pkg'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--no-venv'])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))
            ensure_dir_exists(os.path.join(package_dir, 'data'))

            # add additional files (to exclude for building later)
            touch_file(os.path.join(package_dir, 'data','somefile.txt'))
            touch_file(os.path.join(package_dir, 'local_extra_file.someext.txt'))

            os.chdir(package_dir)

            # check if those files exists
            package_dir_contents = os.listdir(os.path.join(package_dir))
            self.assertTrue('local_extra_file.someext.txt' in package_dir_contents)
            self.assertTrue('data' in package_dir_contents)

            # set exclude_paths in settings
            settings = copy_default_settings()
            settings["exclude_paths"] = ["data", "local_extra_file.*"]
            save_settings(settings, package_dir=package_dir)

            # run the builder
            result = runner.invoke(kecpkg, ['build', pkgname, '--verbose'])
            self.assertEqual(result.exit_code, 0, "Results of the run were: \n---\n{}\n---".format(result.output))
            self.assertExists(os.path.join(package_dir, 'dist'))

            # check the zip such that the extra files are not packaged
            dist_list = os.listdir(os.path.join(package_dir, 'dist'))
            zipfile = ZipFile(os.path.join(package_dir, 'dist', dist_list[0]), 'r')
            contents = zipfile.namelist()

            self.assertFalse('local_extra_file.someext.txt' in contents)
            self.assertFalse('data' in contents)

    def test_build_with_alternate_config(self):
        pkgname = 'new_pkg'
        alt_settings = 'alt-settings.json'

        with temp_chdir() as d:
            runner = CliRunner()
            result = runner.invoke(kecpkg, ['new', pkgname, '--no-venv'])
            package_dir = get_package_dir(pkgname)
            self.assertTrue(os.path.exists(package_dir))

            # set alternative settings path
            settings = copy_default_settings()
            settings["package_name"] = pkgname
            save_settings(settings, package_dir=package_dir, settings_filename=alt_settings)

            os.chdir(package_dir)

            result = runner.invoke(kecpkg, ['build', pkgname, '--config', alt_settings])
            self.assertEqual(result.exit_code, 0, "Results of the run were: \n---\n{}\n---".format(result.output))
            self.assertExists(os.path.join(package_dir, 'dist'))

            dist_dir_contents = os.listdir(os.path.join(package_dir, 'dist'))
            self.assertTrue(len(dist_dir_contents), 1)
            self.assertTrue(pkgname in dist_dir_contents[0],
                            "the name of the pkg `{}` should be in the name of "
                            "the built kecpkg `{}`".format(pkgname, dist_dir_contents[0]))
