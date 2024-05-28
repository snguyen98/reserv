from flask import render_template, Blueprint, g
from flask_login import login_required, LoginManager
from datetime import date, timedelta, datetime

from ..data.db import get_db
from .auth import login_required

main_bp = Blueprint("main", __name__)

@main_bp.route('/')
@login_required
def index():
    g.today = date.today()
    week_start = get_week_start(g.today)
    list_days = [week_start + timedelta(days=i) for i in range(14)]
    schedule = dict.fromkeys(list_days)
    booked_days = get_schedule(list_days[0], list_days[-1])

    for booked_day in booked_days:
        booked_date = datetime.strptime(booked_day["date"], "%Y-%m-%d").date()
        schedule[booked_date] = booked_day["userid"]

    g.schedule = schedule
    
    return render_template('index.html')


def get_schedule(start: date, end: date):
    db = get_db()

    schedule = db.execute(
        "SELECT * FROM schedule WHERE userid IS NOT NULL AND userid != '' AND date BETWEEN ? AND ?", (start,end)
    ).fetchall()

    return schedule


def get_week_start(from_date: date, week_offset: int=0) -> date:
    return from_date + timedelta(days=-from_date.weekday(), weeks=week_offset)


def print_schedule():
    for key, val in g.schedule.items():
        if val is None:
            val = ""
        print(key.strftime('%d/%m') + ": " + val)