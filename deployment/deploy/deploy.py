from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import sys
import os
import shutil
import logging

parser = ArgumentParser(
    description="Deploy new release to production",
    formatter_class=ArgumentDefaultsHelpFormatter
)

# Define default paths
current_dir = os.path.dirname(os.path.realpath(__file__))
src_default_path = os.path.join(current_dir, "app.zip")
log_default_path = os.path.join(current_dir, "logs")

# Parse arguments supplied to the script
parser.add_argument("dest", help="Location to deploy the package")
parser.add_argument("--src", default=src_default_path, nargs="?", help="Location of the source package to deploy")
parser.add_argument("--log", nargs="?", default=log_default_path, help="Location to save deployment logs")
parser.add_argument('--backup', default=True, action='store_true', help="Backup currently deployed app")
parser.add_argument("--no-backup", dest="backup", action='store_false', help="Don't backup currently deployed app")
args = vars(parser.parse_args())

# Define paths to directories
dest_path = os.path.join(args["dest"], "app")
backup_path = os.path.join(args["dest"], "backup")
src_path = args["src"]
log_path = args["log"]

# Attempt to create the log directory if it doesn't already exist
try:
    os.makedirs(log_path)
except:
    pass

# Configure the log to include today's date
today = datetime.today().strftime('%Y%m%d')
log_path = os.path.join(log_path, f"deploy_{today}.log")

# Configure logging
logging.basicConfig(filename=log_path, encoding="utf-8", level=logging.DEBUG, format="%(asctime)s    %(levelname)-8s    %(message)s")

# Define files and folders to ignore when copying
ignore_patterns = shutil.ignore_patterns(
    "__pycache__",
    "instance",
    "*.key",
    "*.db",
    "config.yaml",
    "backup"
)

# Attempt to get the version of the currently deployed app
try:
    version_old_path = os.path.join(dest_path, "version.txt")

    with open(version_old_path, "rt") as f:
        version = f.read()
    
    logging.info(f"Found version {version} of currently deployed app")

except:
    logging.warning("No app currently deployed or version file invalid")
    version = "unknown"

# Attempt to make a backup of the previous version of the app if it exists, excluding the ignore patterns
if args["backup"]:
    try:
        backup_folder = os.path.join(backup_path, f"app_{today}_{version}")

        shutil.copytree(
            dest_path,
            backup_folder,
            ignore=ignore_patterns,
            dirs_exist_ok=False
        )

        logging.info(f"Backed up currently deployed to {backup_folder}")

        shutil.rmtree(dest_path)
        logging.info("Cleared destination path for new release")
        
    except Exception as err:
        logging.error(f"Error: could not create backup, {err}")
        sys.exit()

else:
    logging.info("Skipping creating backup...")

# Attempts to unzip the app package into the destination folder
try:
    shutil.unpack_archive(src_path, dest_path, format="zip")
    logging.info("Successfully deployed new package")

except Exception as err:
    logging.error(f"Error unzipping the app package, {err}")
