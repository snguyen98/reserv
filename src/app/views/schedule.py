from flask import render_template, Blueprint, g
from flask_login import login_required
from datetime import date, timedelta
import logging

from .auth import login_required

schedule_bp = Blueprint("schedule", __name__)

@schedule_bp.route('/')
@login_required
def index():
    g.today = date.today()
    week_start = g.today + timedelta(days=-g.today.weekday(), weeks=0)

    g.schedule = [week_start + timedelta(days=i) for i in range(14)]

    logging.debug(f"Setting schedule for w/c {week_start}")

    return render_template('index.html')
