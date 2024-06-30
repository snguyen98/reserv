from flask import Blueprint, request, session, g
from flask import render_template, flash
from werkzeug.security import generate_password_hash
import logging

from ..data.db import get_db
from ..forms.change_name_form import ChangeName
from ..forms.reset_password_form import ResetPassword
from .auth import login_required

account_bp = Blueprint("account", __name__, url_prefix="/account")

@account_bp.route("/change_name", methods=['GET', 'POST'])
@login_required
def change_name():
    """
    Change user display name based on form submission
    """
    form = ChangeName(request.form)

    if request.method == 'POST' and form.validate():
        try:
            db = get_db()
            db.execute("UPDATE user SET displayname = ? WHERE userid = ? ", (form.new_name.data, g.user["userid"]))
            db.commit()

            flash("Display name changed successfully")

            logging.info(f"Display name for {g.user['userid']} to {form.new_name.data}")

        except Exception as err:
            if "UNIQUE constraint failed" in str(err):
                flash(f"Error: Display name already exists")
                logging.debug(f"Display name for {g.user['userid']} was not changed, name provided already exists")

            else:
                flash("Unknown error changing display name")
                logging.error(f"Error changing display name: {err}")
        
    return render_template('change_name.html', form=form)


@account_bp.route("/reset_password", methods=['GET', 'POST'])
@login_required
def reset_password():
    """
    Reset user password based on form submission
    """
    form = ResetPassword(request.form)

    if request.method == 'POST' and form.validate():
        try:
            hash_new_pass = generate_password_hash(form.new_pass.data)

            db = get_db()
            db.execute("UPDATE user SET password = ? WHERE userid = ? ", (hash_new_pass, g.user["userid"]))
            db.commit()

            flash("Password changed successfully")

            logging.info(f"Password changed for {g.user['userid']} to {hash_new_pass}")

        except Exception as err:
            flash(f"Error resetting password")

            logging.error(f"Error resetting password: {err}")
        
    return render_template('reset_password.html', form=form)