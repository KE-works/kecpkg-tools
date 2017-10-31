

from kecpkg.utils import normalize_package_name

def create_package(kecpkg_dir, package_name, settings):
    """
    Create the package directory

    :param kecpkg_dir: root dir where to create the kecpkg
    :param package_name: name of the package
    :param settings: settings dict
    """

    normalised_package_name = normalise_package_name(package_name)