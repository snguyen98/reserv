import sqlite3
from flask import g
from flask import Flask
import logging

DB_PATH = 'app/data/schedule.db'

def get_db():
    if "db" not in g:
        logging.debug("Opening connection to schedule database...")
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_connection_db():
    db = g.pop("db", None)

    if db is not None:
        db.close()
        logging.debug("Closed connection to schedule database")