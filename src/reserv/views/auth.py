import functools
import logging

from flask import Blueprint, request, session, g, jsonify
from flask import render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash

from ..data.query import get_user_by_id, get_user_status, check_perm
from ..forms.login_form import Login

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    """
    Logs in a registered user by adding the user id to the session
    """
    form = Login(request.form)
    user_id = form.user_id.data
    password = form.password.data

    # Processes the form data if form passes validation and POST request is made
    if request.method == "POST" and form.validate():
        try:
            user = get_user_by_id(user_id)
            error = None

            # Checks if the user id matches a user in the database
            if user is None:
                error = "Incorrect User ID."
                logging.debug(f"User ID, {user_id} not found in database")

            # Checks if the supplied password matches the encrypted password
            elif not check_password_hash(user["password"], password):
                error = "Incorrect password."
                logging.debug(f"Password provided for {user_id} does not " 
                              "match the value in the database")

            if error is None:
                # Stores the user id in a new session and return to the index
                session.clear()
                session["user_id"] = user["user_id"]

                logging.info(f"Logging in as {user_id}...")

                return redirect(url_for("index"))

            flash(error)

        except Exception as err:
            flash(f"Error logging in")
            logging.error(f"Error logging in: {err}")
        
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


@auth_bp.route("/access_denied")
def access_denied():
    """
    Displays the access denied page for users who are inactive or don't have the
    necessary permissions to view the page
    """
    return render_template('access_denied.html')


@auth_bp.before_app_request
def load_logged_in_user():
    """
    If a user id is stored in the session, load the user object from the 
    database into g.user
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
        
    else:
        try:
            g.user = get_user_by_id(user_id)
            g.book_perm = check_perm(id=user_id, perm="book")
            g.manage_perm = check_perm(id=user_id, perm="manage")

        except Exception as err:
            logging.error(f"Error retrieving user, {user_id} from database " 
                          f"with error: {err}")
            g.user = None


def login_required_view(view):
    """
    View decorator used for web views that checks if a user is logged in
    and active, redirects to the login page if not
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logging.debug("Checking if user is logged in (view)...")

        if g.user is None:
            logging.debug("User is not logged in, redirecting to login page...")
            return redirect(url_for("auth.login"))
        
        elif not check_user_active(g.user["user_id"]):
            logging.debug("User is inactive, redirecting to login page...")
            return redirect(url_for("auth.access_denied"))

        else:
            logging.debug("User is logged in")
            return view(**kwargs)

    return wrapped_view


def login_required_ajax(view):
    """
    View decorator used for ajax handlers that checks if a user is logged in
    and active, returns 403 error if not
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        logging.debug("Checking if user is logged in (ajax)...")

        if g.user is None:
            logging.debug("User is not logged in, returning html code 403...")
            return jsonify(message="No user logged in"), 403

        elif not check_user_active(g.user["user_id"]):
            logging.debug("User is inactive, returning html code 403...")
            return jsonify(message="Error: account is inactive"), 403
        
        else:
            logging.debug("User is logged in")
            return view(**kwargs)

    return wrapped_view


def check_user_active(user_id: str) -> bool:
    """
    Checks if user status of the supplied user is active
    """
    return get_user_status(user_id) == "active"