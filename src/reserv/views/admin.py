from flask import render_template, Blueprint, g
import logging
import os

from .auth import login_required_view

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/center')
@login_required_view
def center():
    """
    Displays the version info template
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.join(current_dir, f"../app_version.txt")

    try:
        with open(version_path, "rt") as f:
            g.version = f.read()

        logging.info(f"Found version {g.version} of app")

    except Exception as err:
        logging.error(f"Version file cannot be read, {err}")
        g.version = "Unknown"
    
    return render_template('version_info.html')


def get_version() -> str:
    """
    Get the version of the app to build

    Params
    ------
    src_path        The path of the src folder
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.join(current_dir, f"../app_version.txt")

    try:
        with open(version_path, "rt") as f:
            version = f.read()

        logging.info(f"Found version {version} of app to build")
        return version

    except Exception as err:
        logging.error(f"No app found or version file cannot be read, {err}")
        return None