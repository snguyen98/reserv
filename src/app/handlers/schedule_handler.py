from flask import Blueprint, request, jsonify, session
from datetime import date, datetime, timedelta
import logging

from ..data.db import get_db, close_connection_db

schedule_handler_bp = Blueprint("schedule_handler", __name__, url_prefix="/handlers")

@schedule_handler_bp.route("/get_booker", methods=["GET"])
def get_booker():
    date_arg = request.args.get('date')

    try:
        db = get_db()
        res_booker = db.execute("SELECT userid FROM schedule WHERE date = ?", (date_arg,)).fetchone()

        if res_booker:
            booker_id = res_booker[0]
            res = db.execute("SELECT displayname FROM user WHERE userid = ?", (booker_id,)).fetchone()

            if not res[0] or res[0] == "":
                logging.warning((f"No display name found for user, {booker_id}"))

            ret_val = jsonify(isBooked=True, booker=res[0])
            logging.debug(f"Found booker with display name, {res[0]} for {date_arg}")
        
        else:
            logging.debug(f"No booker found for {date_arg}, displaying date as available")
            ret_val = jsonify(isBooked=False, booker="")

    except Exception as err:
        logging.error(f"Error retrieving booker for {date_arg} with error: {err}")
        ret_val = jsonify(isBooked=False, booker="")

    finally:
        close_connection_db()
        return ret_val
    

@schedule_handler_bp.route("/set_booker", methods=["GET"])
def set_booker():
    date_arg = request.args.get('date')

    if datetime.strptime(date_arg, "%Y-%m-%d").date() < date.today():
        logging.debug(f"Date {date_arg} was not booked for {session.get('user_id')} as booking date is in the past")
        ret_val = jsonify(message="Booking date cannot be in the past"), 403

    elif session.get("user_id") is None:
        logging.debug(f"Date {date_arg} was not booked as no user is logged in")
        ret_val = jsonify(message="Not logged in"), 403

    elif not validate_booking(date_arg):
        logging.debug(f"Date {date_arg} was not booked for {session.get('user_id')} as user has booked at least twice in a seven day period")
        ret_val = jsonify(message="Cannot book more than twice within a seven day period"), 403
        logging.debug(ret_val)

    else:
        try:
            db = get_db()
            db.execute("INSERT INTO schedule (date, userid) VALUES (?,?)", (date_arg, session.get('user_id')))
            db.commit()

            ret_val = jsonify(message="Booked"), 200
            logging.info(f"Successfully booked date {date_arg} for {session.get('user_id')}")
        
        except Exception as err:
            # This error should handle if the date is already booked as well as any other unexpected errors
            logging.error(f"Error booking date {date_arg} for {session.get('user_id')} with error, {err}")
            ret_val = jsonify(message="Something went wrong with this request"), 500
        
    close_connection_db()
    return ret_val


@schedule_handler_bp.route("/cancel_booking", methods=["GET"])
def cancel_booking():
    date_arg = request.args.get('date')

    try:
        db = get_db()
        booked_user = db.execute("SELECT userid FROM schedule WHERE date = ?", (date_arg,)).fetchone()

        if booked_user:
            if session.get("user_id") == booked_user[0]:
                db.execute("DELETE FROM schedule WHERE date = ?", (date_arg,))
                db.commit()

                logging.info(f"Successfully cancelled booking by {booked_user[0]} on {date_arg}")

                ret_val = jsonify(message="Cancelled booking")
            
            else:
                logging.debug(f"Booking on {date_arg} was not cancelled as logged in user {session.get('user_id')} did not match booked user {booked_user[0]}")
                ret_val = jsonify(message="Something went wrong with this request"), 500
        
        else:
            logging.warning(f"Could not cancel booking, no booker found on {date_arg}")
            ret_val = jsonify(message="Something went wrong with this request"), 500

    except Exception as err:
        logging.error(f"Error cancelling booking for {date_arg} with error: {err}"), 500
        ret_val = jsonify(message="Something went wrong with this request"), 500

    finally:
        close_connection_db()
        return ret_val
        

def validate_booking(date_str: str) -> bool:
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    period = 6

    logging.debug(f"Validating bookings from {date_str} for {period}...")

    for i in range(period + 1):
        start_date = date - timedelta(days = i)
        start_date_str = datetime.strftime(start_date, "%Y-%m-%d")
        
        if get_num_bookings(start_date=start_date_str, period=f"{period} days") >= 2:
            return False

    return True


def get_num_bookings(start_date: str, period: str) -> int:
    query = """
        SELECT COUNT(*)
        FROM schedule
        WHERE strftime('%s', date)
        BETWEEN strftime('%s', ?1)
        AND strftime('%s', DATE(?1, ?2))
        AND userid = ?3
    """

    user_id = session.get("user_id")

    try:
        db = get_db()
        res = db.execute(query, (start_date, period, user_id)).fetchone()[0]

    except Exception as err:
        logging.error(f"Error retrieving booking count for {user_id} from {start_date} for {period} with error: {err}")

    finally:
        close_connection_db()

    logging.debug(f"Num bookings: {res} by {user_id} for start date: {start_date}, period: {period}")

    return res