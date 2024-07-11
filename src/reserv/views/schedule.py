from flask import render_template, Blueprint, g
from flask_login import login_required
from datetime import date, timedelta
import logging

from .auth import login_required

schedule_bp = Blueprint("schedule", __name__)

@schedule_bp.route('/')
@login_required
def index():
    """
    Defines g.schedule to be used in the schedule template (index.html)
    """
    g.today = date.today()

    # Calculates the date of the monday of the current week
    week_start = g.today + timedelta(days=-g.today.weekday(), weeks=0)

    # Generates a list of dates from the week start for the next 14 days
    g.schedule = [week_start + timedelta(days=i) for i in range(14)]

    logging.debug(f"Setting schedule for w/c {week_start}")

    return render_template('index.html')
