from flask import render_template, Blueprint, g
from flask_login import login_required
from datetime import date, timedelta

from .auth import login_required

main_bp = Blueprint("main", __name__)

@main_bp.route('/')
@login_required
def index():
    g.today = date.today()
    week_start = g.today + timedelta(days=-g.today.weekday(), weeks=0)

    g.schedule = [week_start + timedelta(days=i) for i in range(14)]

    return render_template('index.html')


def print_schedule():
    for key, val in g.schedule.items():
        if val is None:
            val = ""
        print(key.strftime('%d/%m') + ": " + val)