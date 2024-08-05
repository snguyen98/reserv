from flask import Blueprint, request, jsonify, session, g
from datetime import date, datetime, timedelta
import logging

from ..data.query import get_booking_by_date, get_name_by_id, check_perm
from ..data.query import create_booking, update_booking, get_bookings_by_params
from ..data.query import remove_booking
from ..views.auth import login_required_ajax

schedule_handler_bp = Blueprint(
    "schedule_handler",
    __name__,
    url_prefix="/handlers"
)

@schedule_handler_bp.route("/get_current_user", methods=["GET"])
@login_required_ajax
def get_current_user():
    """
    Handler for returning the display name of the currently logged in user
    """
    logging.info("Getting currently logged in user...")

    user_id = g.user["user_id"]
    res = get_name_by_id(user_id)

    if not res or res["display_name"] == "":
        logging.warning(f"No display name found for user, {user_id}")
        return jsonify(message="Logged in user has no display name"), 403

    name = res["display_name"]

    logging.debug(f"Found name, {name} for id, {user_id}")
    return jsonify(user=name), 200


@schedule_handler_bp.route("/check_perm", methods=["GET"])
@login_required_ajax
def check_user_perm():
    """
    Handler for returning True if the currently logged in user has the manage
    permission, False otherwise
    """
    user_id = g.user["user_id"]
    perm = request.args.get('perm')

    try:
        res = check_perm(user_id, perm)
        logging.info(f"User {user_id} has {perm} permissions: {res}")

        return jsonify(res=res), 200

    except Exception as err:
        logging.error(f"Error when checking permissions for user, {user_id}")
        return jsonify(message="Logged in user has no display name"), 500


@schedule_handler_bp.route("/get_bookers", methods=["GET"])
@login_required_ajax
def get_bookers():
    """
    Handler for returning the display name of the booker assigned to each date
    in the list supplied by the request
    """
    current_user = session.get('user_id')
    dates_arg = request.args.getlist("date_list[]")
    bookings = {}

    logging.debug(f"Getting bookers for {dates_arg}")

    for date in dates_arg:
        try:
            booking = get_booking_by_date(date)

            if booking and booking["status"] == "booked":
                booker = booking["user_id"]
                res = get_name_by_id(booker)

                if not res or res["display_name"] == "":
                    logging.warning(f"No display name found for user, {booker}")

                name = res["display_name"]
                logging.debug(f"Found booker with name, {name} for {date}")
                bookings[date] = {
                    "isBooked": True,
                    "booker": name,
                    "bookPerm": name == current_user
                }
            
            else:
                logging.debug(f"No booker found for {date}")
                bookings[date] = {
                    "isBooked": False,
                    "booker": "",
                    "bookPerm": False
                }

        except Exception as err:
            logging.error(f"Error retrieving booker for {date}, {err}")
            bookings[date] = {
                "isBooked": False,
                "booker": "",
                "bookPerm": False
            }
    
    logging.debug(f"Sending: {bookings}")
    return jsonify(res=bookings)
    

@schedule_handler_bp.route("/set_booker", methods=["GET"])
@login_required_ajax
def set_booker():
    """
    Handler for setting the booker to the currently logged in user to the date
    supplied by the request
    """
    date_arg = request.args.get('date')
    current_user = session.get('user_id')

    # Checks if they have valid permissions to book
    if not check_perm(current_user, "book"):
        logging.debug(f"{current_user} could not book {date_arg} as they don't "
                      "have book permissions")
        return jsonify(message="You do not have permission to book, please log "
                       "in as a user"), 403
    # Checks if the booking is valid
    elif datetime.strptime(date_arg, "%Y-%m-%d").date() < date.today():
        logging.debug(f"Date {date_arg} was not booked for {current_user} as "
                      "booking date is in the past")
        return jsonify(message="Booking date cannot be in the past"), 403

    elif not validate_booking(date_arg):
        logging.debug(f"Date {date_arg} was not booked for {current_user} as "
                      "user has booked at least twice in a seven day period")
        return jsonify(message=f"Cannot book more than twice within a seven "
                       "day period"), 403

    else:
        try:
            booking = get_booking_by_date(date_arg)

            if booking:
                if booking["status"] != 'booked':
                    update_booking(date=date_arg, id=current_user)

                else:
                    logging.info(f"Could not book date {date_arg} for "
                                 f"{current_user} as it is already booked")
                    return jsonify(message="Date is already booked"), 403
                
            else:
                create_booking(date=date_arg, id=current_user)

            logging.info(f"Booked date {date_arg} for {current_user}")
            return jsonify(message="Booked"), 200
            
        except Exception as err:
            logging.error(f"Error booking date {date_arg} for {current_user} "
                          f"with error, {err}")
            return jsonify(message="Something went wrong with the request"), 500


@schedule_handler_bp.route("/cancel_booking", methods=["GET"])
@login_required_ajax
def cancel_booking():
    """
    Handler for cancelling the booking on the supplied date if the booker 
    matches the currently logged in user
    """
    date_arg = request.args.get('date')
    curr_user = session.get('user_id')

    # Checks if the date can be cancelled first
    if datetime.strptime(date_arg, "%Y-%m-%d").date() < date.today():
        logging.debug(f"Date {date_arg} was not cancelled for {curr_user} " 
                      "as cancel date is in the past")
        return jsonify(message="Cancel date cannot be in the past"), 403
    
    else:
        try:
            booking = get_booking_by_date(date_arg)

            # Checks if the date is booked
            if booking:
                booking_user = booking["user_id"]
                # Checks if the user on the booking matches the user logged in
                if curr_user == booking_user or check_perm(curr_user, "manage"):
                    remove_booking(date=date_arg)

                    logging.info(f"Cancelled booking by {booking_user} on "
                                 f"{date_arg}")
                    return jsonify(message="Cancelled booking")
                
                else:
                    logging.debug(f"Booking on {date_arg} was not cancelled as "
                                  f"logged in user {curr_user} did not match"
                                  f" booked user {booking_user}")
                    return jsonify(
                        message="Something went wrong with the request"), 500
            
            else:
                logging.warning("Could not cancel booking, no booker found " 
                                f"on {date_arg}")
                return jsonify(
                    message="Something went wrong with this request"), 500

        except Exception as err:
            logging.error(f"Error cancelling booking for {date_arg} with " 
                          f"error, {err}"), 500
            return jsonify(message="Something went wrong with the request"), 500
            

def validate_booking(date_str: str) -> bool:
    """
    Checks if there would be any 7 day periods where there are more than 3
    bookings made by the logged in user if they book the supplied date

    Params
    ------
    date_str        The date the user wants to book
    """
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    # The query excludes the booking date itself so it validates a 7 day period
    period = 6

    logging.debug(f"Validating bookings from {date_str} for {period}...")

    # Loops through every possible 7 day period
    for i in range(period + 1):
        start_date = date - timedelta(days = i)
        start_date_str = datetime.strftime(start_date, "%Y-%m-%d")

        num_bookings = get_num_bookings(start_date=start_date_str, 
                                        period=f"{period} days")
        
        if num_bookings >= 2:
            return False

    return True


def get_num_bookings(start_date: str, period: str) -> int:
    """
    Checks the number of bookings made by the logged in user from a given date
    for a given number of days from that date

    Params
    ------
    start_date          The date at which to begin the query
    period              The number of days from the start date
    """
    user_id = session.get("user_id")

    try:
        res = get_bookings_by_params(date=start_date, period=period, id=user_id)

    except Exception as err:
        logging.error(f"Error retrieving booking count for {user_id} from "
                      f"{start_date} for {period} with error: {err}")

    logging.debug(f"Num bookings: {res} by {user_id} for start date: " 
                  f"{start_date}, period: {period}")
    return res