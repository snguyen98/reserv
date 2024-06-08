from flask import Blueprint, request, session
from flask import render_template, flash
from werkzeug.security import generate_password_hash

from ..data.db import get_db
from ..forms.change_name_form import ChangeName
from ..forms.reset_password_form import ResetPassword

account_bp = Blueprint("account", __name__, url_prefix="/account")


@account_bp.route("/change_name", methods=['GET', 'POST'])
def change_name():
    """
    Change user display name based on form submission
    """
    form = ChangeName(request.form)

    if request.method == 'POST' and form.validate():
        try:
            db = get_db()
            db.execute("UPDATE user SET displayname = ? WHERE userid = ? ", (form.new_name.data, (session.get("user_id"))))
            db.commit()

            flash("Display name changed successfully")

        except Exception:
            flash(f"Error changing display name")
        
    return render_template('change_name.html', form=form)


@account_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    """
    Reset user password based on form submission
    """
    form = ResetPassword(request.form)

    if request.method == 'POST' and form.validate():
        try:
            hash_new_pass = generate_password_hash(form.new_pass.data)

            db = get_db()
            db.execute("UPDATE user SET password = ? WHERE userid = ? ", (hash_new_pass, (session.get("user_id"))))
            db.commit()

            flash("Password changed successfully")

        except Exception:
            flash(f"Error resetting password")
        
    return render_template('reset_password.html', form=form)