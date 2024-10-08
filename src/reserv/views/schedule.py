from flask import render_template, Blueprint, g
from datetime import date, timedelta
import logging

from .auth import login_required_view
from ..data.query import check_perm

schedule_bp = Blueprint("schedule", __name__)

@schedule_bp.route('/')
@login_required_view
def index():
    """
    Defines g.schedule to be used in the schedule template (index.html)
    """
    user_id = g.user["user_id"]

    if check_perm(user_id, "view"):
        g.today = date.today()

        # Calculates the date of the monday of the current week
        week_start = g.today + timedelta(days=-g.today.weekday(), weeks=0)

        # Generates a list of dates from the week start for the next 14 days
        g.schedule = [week_start + timedelta(days=i) for i in range(14)]

        logging.debug(f"Setting schedule for w/c {week_start}")

        return render_template('index.html')
    
    else:
        return render_template('access_denied.html')
