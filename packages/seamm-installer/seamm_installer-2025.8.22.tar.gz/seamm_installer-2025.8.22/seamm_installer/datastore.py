# -*- coding: utf-8 -*-

"""Handle the datastore for SEAMM."""

import importlib.metadata as implib
from pathlib import Path
import platform
import subprocess

from . import my


system = platform.system()
if system in ("Darwin",):
    from .mac import ServiceManager

    mgr = ServiceManager(prefix="org.molssi.seamm.")
elif system in ("Linux",):
    from .linux import ServiceManager

    mgr = ServiceManager(prefix="org.molssi.seamm.")
else:
    raise NotImplementedError(f"SEAMM does not support services on {system} yet.")


def setup(parser):
    """Define the command-line interface for handling services.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The main parser for the application.
    """
    services_parser = parser.add_parser("datastore")
    subparser = services_parser.add_subparsers()

    # Show
    tmp_parser = subparser.add_parser("show")
    tmp_parser.set_defaults(func=show)

    # Update
    tmp_parser = subparser.add_parser("update")
    tmp_parser.set_defaults(func=update)


def latest_version():
    """Show information about the datastore."""
    path = _find_path()
    version = None
    if path is not None:
        cmd = "alembic heads"
        result = subprocess.run(
            cmd, cwd=path, shell=True, text=True, capture_output=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
        else:
            my.logger.warning(f"Running '{cmd}' was not successful:")
            my.logger.warning(result.stderr)
    return version


def db_version():
    """Return the version of the database."""
    db_path = Path(my.options.root) / "Jobs" / "seamm.db"
    if not db_path.expanduser().exists():
        version = "not installed"
    else:
        path = _find_path()
        version = "unknown"
        if path is not None:
            uri = f"sqlite:///{str(db_path.expanduser())}"
            cmd = f'alembic -x uri="{uri}" current'
            result = subprocess.run(
                cmd, cwd=path, shell=True, text=True, capture_output=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                if version == "":
                    version = "--none--"
            else:
                my.logger.warning(f"Running '{cmd}' was not successful:")
                my.logger.warning(result.stderr)
    return version


def update():
    """Update the database to the latest version."""
    db_path = Path(my.options.root) / "Jobs" / "seamm.db"
    if not db_path.expanduser().exists():
        print(f"The database file '{db_path}' does not exist.")
    else:
        version = db_version()
        latest = latest_version()
        if version == latest:
            print(f"The database at '{db_path}' is already up-to-date.")
        else:
            service_name = "dev_dashboard" if my.development else "dashboard"
            restart = mgr.is_running(service_name)
            if restart:
                print(f"Stopping the service {service_name}")
                mgr.stop_service(service_name)

            print("Updating the database.")
            update_db()

            if restart:
                print(f"Restarting the service {service_name}")
                mgr.start_service(service_name)

            version = db_version()
            if version == latest:
                print(
                    f"The database at '{db_path}' has been updated to version {version}"
                )
            else:
                raise RuntimeError(
                    f"The database at '{db_path}' was updated to version {version},\n"
                    f"but it should be {latest}. Something went wrong!"
                )


def update_db():
    """Update the database to the latest version."""
    db_path = Path(my.options.root) / "Jobs" / "seamm.db"
    if not db_path.expanduser().exists():
        raise RuntimeError(f"The database '{db_path}' does not exist.")

    path = _find_path()
    if path is None:
        raise RuntimeError(
            "Cannot find the path to the installed version of seamm-datastore.\n"
            "Is it installed?"
        )
    uri = f"sqlite:///{str(db_path.expanduser())}"
    cmd = f'alembic -x uri="{uri}" upgrade head'
    result = subprocess.run(cmd, cwd=path, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Running '{cmd}' was not successful:\n\n{result.stderr}")


def show():
    """Show information about the datastore."""
    db_path = Path(my.options.root) / "Jobs" / "seamm.db"
    latest = latest_version()
    if not db_path.expanduser().exists():
        print(f"The database file '{db_path}' does not exist.")
    else:
        version = db_version()
        if version == latest:
            print(f"The database at '{db_path}' (version {version}) is up-to-date.")
        else:
            print(
                f"The database at '{db_path}' (version {version}) should be upgraded "
                f"to {latest} by running"
                "\n\n"
                "          seamm-installer datastore update"
            )


def _find_path():
    """Return the path for alembic in the datastore installation.

    Returns
    -------
    pathlib.Path
        The path to the alembic installation, or None if not present.
    """
    files = [p for p in implib.files("seamm-datastore") if "alembic.ini" in str(p)]
    if len(files) == 0:
        path = None
    else:
        path = files[0].locate().parent

    return path
