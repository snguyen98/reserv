from flask import g, current_app
from flask.cli import with_appcontext
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
@with_appcontext
def init_db():
    """ Initialises the database from schema file """
    db = get_db()

    with current_app.open_resource("data/schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

    click.echo("Initialised the database")


@click.command("create-user")
@click.argument("id")
@click.argument("name")
@click.argument("password")
@with_appcontext
def create_user(id, name, password):
    """ Creates a new user """

    hash_password = generate_password_hash(password)

    try:
        db = get_db()
        db.execute("INSERT INTO user (userid, displayname, password) VALUES (?,?,?)", (id, name, hash_password,))
        db.commit()

        click.echo(f"Successfully created user with ID {id}")
        logging.info(f"Successfully created user with ID {id}")

    except Exception as err:
        click.echo(f"An error occurred when creating the user, {err}")
        logging.error(f"Error creating user, {err}")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
    app.cli.add_command(create_user)