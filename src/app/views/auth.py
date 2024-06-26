import functools

from flask import Blueprint, request, session, g
from flask import render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash
from ..data.db import get_db, close_connection_db
from ..forms.login_form import Login
import logging

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


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
                logging.debug(f"User ID, {form.user_id.data} not found in database")

            elif not check_password_hash(user["password"], form.password.data):
                error = "Incorrect password."
                logging.debug(f"Password provided for {form.user_id.data} does not match the value in the database")

            if error is None:
                # store the user id in a new session and return to the index
                session.clear()
                session["user_id"] = user["userid"]

                logging.info(f"Logging in as {form.user_id.data}...")

                return redirect(url_for("index"))

            flash(error)

        except Exception as err:
            flash(f"Error logging in")
            logging.error(f"Error logging in: {err}")

        finally:
            close_connection_db()
        
    return render_template("login.html", form=form)


@auth_bp.route("/logout")
def logout():
    """
    Clear the current session, including the stored user id
    """
    user_id = session.get("user_id")
    session.clear()

    logging.info(f"Cleared session for {user_id}")

    return redirect(url_for("auth.login"))


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
        try:
            db = get_db()
            g.user = db.execute("SELECT * FROM user WHERE userid = ?", (user_id,)).fetchone()

        except Exception as err:
            logging.error(f"Error retrieving user, {user_id} from database with error: {err}")

        finally:
            close_connection_db()


def login_required(view):
    """
    View decorator that redirects anonymous users to the login page
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logging.debug("Checking if user is logged in...")

        if g.user is None:
            logging.debug("User is not logged in, redirecting to login page...")
            return redirect(url_for("auth.login"))

        else:
            logging.debug("User is logged in")
            return view(**kwargs)

    return wrapped_view