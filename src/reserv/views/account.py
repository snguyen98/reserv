from flask import Blueprint, request, g
from flask import render_template, flash
from werkzeug.security import generate_password_hash
import logging

from ..data.query import update_name, update_password
from ..forms.change_name_form import ChangeName
from ..forms.reset_password_form import ResetPassword
from .auth import login_required_view

account_bp = Blueprint("account", __name__, url_prefix="/account")

@account_bp.route("/change_name", methods=['GET', 'POST'])
@login_required_view
def change_name():
    """
    Change user display name based on form submission
    """
    form = ChangeName(request.form)
    current_user = g.user["user_id"]
    new_name = form.new_name.data

    # Processes the form data if form passes validation and POST request is made
    if request.method == 'POST' and form.validate():
        try:
            update_name(id=current_user, name=new_name)

            flash("Display name changed successfully")

            logging.info(f"Display name for {current_user} to {new_name}")

        except Exception as err:
            # Displays corresponding error to the page
            if "UNIQUE constraint failed" in str(err):
                flash(f"Error: Display name already exists")
                logging.debug(f"Display name for {current_user} was not " 
                              "changed, name provided already exists")

            else:
                flash("Unknown error changing display name")
                logging.error(f"Error changing display name: {err}")
        
    return render_template('change_name.html', form=form)


@account_bp.route("/reset_password", methods=['GET', 'POST'])
@login_required_view
def reset_password():
    """
    Reset user password based on form submission
    """
    form = ResetPassword(request.form)
    current_user = g.user["user_id"]

    # Processes the form data if form passes validation and POST request is made
    if request.method == 'POST' and form.validate():
        try:
            hash_pass = generate_password_hash(form.new_pass.data)
            update_password(id=current_user, password=hash_pass)

            flash("Password changed successfully")

            logging.info(f"Password changed for {current_user} to {hash_pass}")

        except Exception as err:
            flash(f"Error resetting password")

            logging.error(f"Error resetting password: {err}")
        
    return render_template('reset_password.html', form=form)