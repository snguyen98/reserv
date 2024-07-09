from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import shutil
import os
import logging
import sys

parser = ArgumentParser(
    description="Deploy release to production",
    formatter_class=ArgumentDefaultsHelpFormatter
)

# Define default paths
current_dir = os.path.dirname(os.path.realpath(__file__))
log_default_path = os.path.join(current_dir, "logs")

parser.add_argument("src", help="Location of the app to build")
parser.add_argument("dest", help="Location to store the build")
parser.add_argument("--log", nargs="?", default=log_default_path, help="Location to save deployment logs")
args = parser.parse_args()

# Define paths to directories
current_dir = os.path.dirname(os.path.realpath(__file__))
temp_path = os.path.join(current_dir, "temp")
deploy_script_path = os.path.join(current_dir, "deploy.py")
src_path = args["src"]
log_path = args["log"]
version_path = os.path.join(src_path, "version.txt")

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

# Get the version of the app to build
try:
    with open(version_path, "rt") as f:
        version = f.read()

    logging.info(f"Found version {version} of app to build")

except Exception as err:
    logging.error(f"No app found or version file cannot be read, {err}")

# Add the app version to the destination path
dest_path = os.path.join(args["dest"], version)

# Delete the destination path if it already exists
try:
    shutil.rmtree(dest_path)
    logging.info(f"Destination folder at {dest_path} found. Removing folder...")
except:
    pass

# Delete the temp folder if it exists
try:
    shutil.rmtree(temp_path)
    logging.info(f"Temp folder at {temp_path} found. Removing folder...")
except:
    pass

# Create the temp folder for zipping files
try:
    os.makedirs(temp_path)
    logging.info(f"New temp folder at {temp_path} created")
except Exception as err:
    logging.error(f"Unable to create temp folder, {err}")
    sys.exit()

# Define files and folders to ignore when copying
ignore_patterns = shutil.ignore_patterns(
    "__pycache__",
    "instance",
    "*.key",
    "*.db",
    "config.yaml"
)

# Attempt to create a copy of the current app, excluding the ignore patterns and archive into a zip file
try:
    shutil.copytree(src_path, dest_path, ignore=ignore_patterns)
    shutil.make_archive(base_name=os.path.join(temp_path, "app"), format="zip", root_dir=os.path.join(dest_path, "app"))
    logging.info(f"Created build for version {version}")

    shutil.rmtree(os.path.join(dest_path, "app"))
    logging.info(f"Deleted temporary copy of app in {dest_path}")

except Exception as err:
    logging.error(f"Could not create a zipped archive of the app, {err}")
    sys.exit()

# Copy deploy script to temp folder and archive into a zip file with the build
try:
    shutil.copy(deploy_script_path, temp_path)
    shutil.make_archive(base_name=os.path.join(dest_path, f"app-release-{version}"), format="zip", root_dir=temp_path)
    logging.info(f"Created app release for version {version}")

    shutil.rmtree(temp_path)
    logging.info(f"Deleted temp folder at {temp_path}")

except Exception as err:
    logging.warning(f"Error creating zipped archive for release, {err}")

# Generate readme instructions for deployment
readme_path = os.path.join(dest_path, "readme.txt")

try:
    with open(readme_path, "w") as file:
        file.write("Instructions for deployment:\n")
        file.write("1. Copy file app-release-[version].zip from the releases folder to your environment.\n")
        file.write("2. Unzip the contents.")
        file.write("3. Using bash or command prompt, navigate to the directory of the unzipped contents.\n")
        file.write("4. Run the script deploy.py. Use 'python deploy.py --help' to see the list of supplied arguments. This script will:\n")
        file.write("    a. Create a backup of your current application if it exists in the folder backup/app_<DATE>_<VERSION>.\n")
        file.write("    b. Unzip the app.zip file containing the release to deploy into the supplied location.\n")
        file.write("    c. Clean up any files used for deployment.\n")
        file.write("5. Run the application. Please refer to the flask documentation for deploying to production: https://flask.palletsprojects.com/en/2.3.x/deploying/") 

    logging.info("Generated readme instructions for deployment")

except Exception as err:
    logging.warning(f"Could not create readme file, {err}")
    
# TODO
# - Separate code into functions