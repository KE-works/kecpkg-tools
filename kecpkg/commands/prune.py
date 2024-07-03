import os

import click

from kecpkg.commands.utils import CONTEXT_SETTINGS
from kecpkg.settings import load_settings
from kecpkg.utils import (
    get_package_name,
    get_package_dir,
    remove_path,
    echo_failure,
    echo_warning,
)


@click.command(
    context_settings=CONTEXT_SETTINGS, short_help="Removes a project's build artifacts"
)
@click.argument("package", required=False)
@click.option(
    "--force", "-f", is_flag=True, help="Forcefully removes the project build artifacts"
)
def prune(package, **options):
    """Remove a project's build artifacts."""
    package_name = package or get_package_name() or click.prompt("Provide package name")
    package_dir = get_package_dir(package_name)

    settings = load_settings(package_name)
    # ensure build directory is there
    build_dir = settings.get("build_dir", "dist")
    build_path = os.path.join(package_dir, build_dir)

    if os.path.exists(build_path):
        if options.get("force") or click.confirm(
            f"Do you want to prune build artifacts for package '{package_name}'?"
        ):
            remove_path(build_path)
            if os.path.exists(build_path):
                echo_failure(f"Something went wrong pruning pacakage `{package_name}`")
        else:
            echo_warning(f"Package `{package_name}` will not be pruned")
    else:
        echo_failure(f"Package `{package_name}` does not exist")
