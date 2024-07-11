from flask import g, current_app
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

import sqlite3
import logging
import click

def get_db():
    """
    Establishes a connection to the database and attaches it to g
    """
    if "db" not in g:
        logging.debug("Opening connection to schedule database...")
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Closes the connection to the database and removes it from g
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()
        logging.debug("Closed connection to schedule database")


@click.command("init-db")
@with_appcontext
def init_db():
    """
    Defines a click command that initialises the database from schema file
    """
    db = get_db()

    with current_app.open_resource("data/schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

    click.echo("Initialised the database")


def init_app(app):
    """
    Registers database functions with the Flask app

    Params
    ------
    app         The Flask app to register to
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
    app.cli.add_command(create_user)


@click.command("create-user")
@click.argument("id")
@click.argument("name")
@click.argument("password")
@with_appcontext
def create_user(id, name, password):
    """
    Defines a click command to create a new user to the database

    Params
    ------
    id              The user id of the user
    name            The display name of the user
    password        The password of the user
    """
    hash_password = generate_password_hash(password)

    try:
        add_user(id=id, name=name, hash_password=hash_password)

        click.echo(f"Successfully created user with ID {id}")
        logging.info(f"Successfully created user with ID {id}")

    except Exception as err:
        click.echo(f"An error occurred when creating the user, {err}")
        logging.error(f"Error creating user, {err}")


def add_user(id: str, name: str, hash_password: str):
    query = "INSERT INTO user (userid, displayname, password) VALUES (?,?,?)"
    db = get_db()
    db.execute(query, (id, name, hash_password,))
    db.commit()