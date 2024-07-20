from flask import g, current_app
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

import sqlite3
import logging
import click
import os

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
    db_dir = os.path.dirname(current_app.config["DATABASE"])

    try:
        os.makedirs(db_dir)
    except:
        pass

    try:
        db = get_db()
        version = get_release_db_version()

        with current_app.open_resource(f"data/schema_v{version}.sql") as f:
            db.executescript(f.read().decode("utf8"))

        click.echo("Initialised the database")
        logging.info("Successfully initialised the database")
    
    except Exception as err:
        click.echo("Error initialising the database")
        logging.error(f"Error initialising database, {err}")


@click.command("upgrade-db")
@with_appcontext
def upgrade_db():
    """
    Defines a click command that upgrades the database to the latest version
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    upgrades_dir = os.path.join(current_dir, "./upgrades")
    
    try:
        release_ver = get_release_db_version()
    except Exception as err:
        logging.error(f"Could read the app database version, {err}")
        click.echo("Error reading the app database version")
        return
    
    instance_ver = get_db_version()
    
    while instance_ver < release_ver:
        upgrade_ver = instance_ver + 1
        upgrade_path = os.path.join(upgrades_dir, f"upgrade_v{upgrade_ver}.sql")

        try:
            db = get_db()
            
            with open(os.path.join(upgrade_path)) as f:
                db.executescript(f.read())

            update_db_version(upgrade_ver)

            logging.info(f"Successfully upgraded database version from "
                         f"{instance_ver} to {upgrade_ver}")
            click.echo(f"Successfully upgraded database version from "
                       f"{instance_ver} to {upgrade_ver}")

            instance_ver = get_db_version()

        except Exception as err:
            logging.error(f"Failed to upgrade from {instance_ver} to "
                          f"{upgrade_ver}, {err}")
            click.echo(f"Error upgrading database version from {instance_ver} "
                       f"to {upgrade_ver}")
            return
            
    instance_ver = get_db_version()
    
    logging.info(f"Database schema upgrade finished, current: {instance_ver}")
    click.echo(f"Database schema upgrade finished, current: {instance_ver}")
    

def get_release_db_version():
    """
    Gets the version of the schema in line with the release deployed
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.join(current_dir, "../db_version.txt")

    with open(version_path, "rt") as f:
        release_ver = int(f.read())

    return release_ver


def get_db_version() -> int:
    """
    Queries the database for it's current version
    """
    db = get_db()
    query = "PRAGMA user_version"
    res = db.execute(query).fetchone()
    return res[0]


def update_db_version(version: int):
    """
    Updates the database version to the supplied version number

    Params
    ------
    version     The version number as integer to update the database to
    """
    db = get_db()
    query = "PRAGMA user_version = {v:d}".format(v=version)
    db.execute(query)


def init_app(app):
    """
    Registers database functions with the Flask app

    Params
    ------
    app         The Flask app to register to
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
    app.cli.add_command(upgrade_db)
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
    query = "INSERT INTO user (user_id, display_name, password) VALUES (?,?,?)"
    db = get_db()
    db.execute(query, (id, name, hash_password,))
    db.commit()