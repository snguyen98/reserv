from flask import Blueprint, request, jsonify, session
from datetime import date, datetime, timedelta
import logging

from ..data.db import get_db

logger = logging.getLogger(__name__)
schedule_bp = Blueprint("schedule", __name__, url_prefix="/handlers")


@schedule_bp.route("/get_booker", methods=["GET"])
def get_booker():
    db = get_db()

    date_arg = request.args.get('date')
    res_booker = db.execute("SELECT userid FROM schedule WHERE date = ?", (date_arg,)).fetchone()

    if res_booker:
        booker_id = res_booker[0]
        res = db.execute("SELECT displayname FROM user WHERE userid = ?", (booker_id,)).fetchone()
    
        if res:
            return jsonify({"res": res[0]})
        
        else:
            return jsonify({"res": ""})
    else:
        return jsonify({"res": ""})
    

@schedule_bp.route("/set_booker", methods=["GET"])
def set_booker():
    db = get_db()

    date_arg = request.args.get('date')

    if datetime.strptime(date_arg, "%Y-%m-%d").date() < date.today():
        return jsonify(message="Booking date cannot be in the past"), 403

    elif session.get("user_id") is None:
        return jsonify(message="Not logged in"), 403

    elif not validate_booking(date_arg):
        return jsonify(message="Cannot book more than twice within a seven day period"), 403

    else:
        try:
            db.execute("INSERT INTO schedule (date, userid) VALUES (?,?)", (date_arg, session.get("user_id")))
            db.commit()
        
        except Exception as err:
            return jsonify(message=f"Error performing booking: {err}"), 400

    return jsonify(message="Booked"), 200


def validate_booking(date_str: str) -> bool:
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    for i in range(7):
        start_date = date - timedelta(days = i)
        start_date_str = datetime.strftime(start_date, "%Y-%m-%d")
        
        if get_num_bookings(start_date=start_date_str, period="6 days") >= 2:
            return False

    return True


def get_num_bookings(start_date: str, period: str) -> int:
    db = get_db()

    query = """
        SELECT COUNT(*)
        FROM schedule
        WHERE strftime('%s', date)
        BETWEEN strftime('%s', ?1)
        AND strftime('%s', DATE(?1, ?2))
        AND userid = ?3
    """

    res = db.execute(query, (start_date, period, session.get("user_id"))).fetchone()[0]

    logger.debug(f"Num bookings: {res} for start date: {start_date}, period: {period}")

    return res

@schedule_bp.route("/cancel_booking", methods=["GET"])
def cancel_booking():
    db = get_db()

    date_arg = request.args.get('date')
    booked_user = db.execute("SELECT userid FROM schedule WHERE date = ?", (date_arg,)).fetchone()

    if booked_user and session.get("user_id") == booked_user[0]:
        db.execute("DELETE FROM schedule WHERE date = ?", (date_arg,))
        db.commit()

        return jsonify(success=True)
    else:
        return jsonify(success=False)