import functools

from flask import Blueprint, request, session, g
from flask import render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash
from ..data.db import get_db
from ..forms.login_form import Login

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):
    """
    View decorator that redirects anonymous users to the login page
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view

@auth_bp.before_app_request
def load_logged_in_user():
    """
    If a user id is stored in the session, load the user object from
    the database into g.user
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE userid = ?", (user_id,)).fetchone()
        )

@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    """
    Log in a registered user by adding the user id to the session
    """
    form = Login(request.form)

    if request.method == "POST" and form.validate():
        try:
            db = get_db()
            user = db.execute("SELECT * FROM user WHERE userid = ?", (form.user_id.data,)).fetchone()

            error = None

            if user is None:
                error = "Incorrect User ID."
            elif not check_password_hash(user["password"], form.password.data):
                error = "Incorrect password."

            if error is None:
                # store the user id in a new session and return to the index
                session.clear()
                session["user_id"] = user["userid"]

                return redirect(url_for("index"))

            flash(error)

        except Exception:
            flash(f"Error logging in")
        
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
def logout():
    """
    Clear the current session, including the stored user id
    """
    session.clear()
    return redirect(url_for("auth.login"))