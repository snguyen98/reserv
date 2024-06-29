from flask import g, current_app
from werkzeug.security import generate_password_hash

import sqlite3
import logging
import click

def get_db():
    if "db" not in g:
        logging.debug("Opening connection to schedule database...")
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()
        logging.debug("Closed connection to schedule database")


@click.command("init-db")
def init_db():
    db = get_db()

    with current_app.open_resource("data/schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

    click.echo("Initialised the database")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)