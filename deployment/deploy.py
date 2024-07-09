from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import sys
import os
import shutil
import logging

# Define constants
APP_NAME = "app"


def create_backup(dest_path: str, backup_path: str, version: str, today: str):
    """
    Create a backup of the previous version of the app, excluding the ignore patterns
    
    Params
    ------
    dest_path       The path where the release will be saved
    backup_path     The path where the backup should be saved
    version         The version of the build
    today           The date today
    """
    try:
        backup_folder = os.path.join(backup_path, f"{APP_NAME}_{today}_{version}")

        shutil.copytree(dest_path, backup_folder, ignore=generate_ignore_patterns(), dirs_exist_ok=False)
        logging.info(f"Backed up currently deployed to {backup_folder}")

        shutil.rmtree(dest_path)
        logging.info("Cleared destination path for new release")

    except Exception as err:
        logging.error(f"Could not create backup, {err}")
        sys.exit()


def deploy_release(dest_path: str, src_path: str):
    """
    Attempts to unzip the app package into the destination folder

    Params
    ------
    dest_path       The path where the release will be saved
    src_path        The path of the src folder
    """
    try:
        shutil.unpack_archive(src_path, dest_path, format="zip")
        logging.info("Successfully deployed new package")

    except Exception as err:
        logging.error(f"Error unzipping the app package, {err}")


def get_version(dest_path: str) -> str:
    """
    Get the version of the app to build

    Params
    ------
    dest_path        The path of the currently deployed app
    """
    version_path = os.path.join(dest_path, "version.txt")

    try:
        with open(version_path, "rt") as f:
            version = f.read()

        logging.info(f"Found version {version} of app to build")
        return version

    except:
        logging.warning(f"No app currently deployed or version file invalid at {version_path}")
        return "unknown"


def generate_ignore_patterns():
    """
    Define files and folders to ignore when copying
    """
    ignore_patterns = shutil.ignore_patterns(
        "__pycache__",
        "instance",
        "*.key",
        "*.db",
        "config.yaml",
        "backup"
    )
    return ignore_patterns


def configure_log(log_path: str, today: str):
    """
    Sets up directories and basic configuration for logging

    Params
    ------
    log_path        The path where the log file should be created
    today           The date today
    """
    # Attempt to create the log directory if it doesn't already exist
    try:
        os.makedirs(log_path)
    except:
        pass

    # Set the log file to include today's date
    log_path = os.path.join(log_path, f"deploy_{today}.log")

    # Configure logging
    logging.basicConfig(filename=log_path, encoding="utf-8", level=logging.DEBUG, format="%(asctime)s    %(levelname)-8s    %(message)s")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Deploy new release to production",
        formatter_class=ArgumentDefaultsHelpFormatter
    )

    # Define default paths
    current_dir = os.path.dirname(os.path.realpath(__file__))
    src_default_path = os.path.join(current_dir, f"{APP_NAME}.zip")
    log_default_path = os.path.join(current_dir, "logs")

    # Parse arguments supplied to the script
    parser.add_argument("dest", help="Location to deploy the package")
    parser.add_argument("--src", default=src_default_path, nargs="?", help="Location of the source package to deploy")
    parser.add_argument("--log", nargs="?", default=log_default_path, help="Location to save deployment logs")
    parser.add_argument('--backup', default=True, action='store_true', help="Backup currently deployed app")
    parser.add_argument("--no-backup", dest="backup", action='store_false', help="Don't backup currently deployed app")
    args = vars(parser.parse_args())

    # Define paths to directories
    dest_path = os.path.join(args["dest"], APP_NAME)
    backup_path = os.path.join(args["dest"], "backup")
    src_path = args["src"]
    log_path = args["log"]

    today = datetime.today().strftime('%Y%m%d')
    configure_log(log_path=log_path, today=today)
    
    if args["backup"]:
        version = get_version(dest_path)
        create_backup(dest_path=dest_path, backup_path=backup_path, version=version, today=today)
    else:
        logging.info("Skipping creating backup...")

    deploy_release(dest_path=dest_path, src_path=src_path)

