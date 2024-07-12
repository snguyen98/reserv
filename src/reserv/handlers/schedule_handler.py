from flask import Blueprint, request, jsonify, session
from datetime import date, datetime, timedelta
import logging

from ..data.query import get_user_by_date, get_name_by_id
from ..data.query import create_booking, remove_booking, get_bookings_by_params

schedule_handler_bp = Blueprint(
    "schedule_handler",
    __name__,
    url_prefix="/handlers"
)

@schedule_handler_bp.route("/get_booker", methods=["GET"])
def get_booker():
    """
    Handler for returning the display name of the booker assigned to the date
    supplied by the request
    """
    date_arg = request.args.get('date')

    try:
        res_booker = get_user_by_date(date_arg)

        if res_booker:
            booker_id = res_booker[0]
            res = get_name_by_id(booker_id)

            if not res[0] or res[0] == "":
                logging.warning(f"No display name found for user, {booker_id}")

            logging.debug(f"Found booker with name, {res[0]} for {date_arg}")
            return jsonify(isBooked=True, booker=res[0])
        
        else:
            logging.debug(f"No booker found for {date_arg}")
            return jsonify(isBooked=False, booker="")

    except Exception as err:
        logging.error(f"Error retrieving booker for {date_arg}, {err}")
        return jsonify(isBooked=False, booker="")
    

@schedule_handler_bp.route("/set_booker", methods=["GET"])
def set_booker():
    """
    Handler for setting the booker to the currently logged in user to the date
    supplied by the request
    """
    date_arg = request.args.get('date')
    current_user = session.get('user_id')

    # Checks if the booking is valid first
    if session.get("user_id") is None:
        logging.debug(f"Date {date_arg} was not booked as no user is logged in")
        return jsonify(message="Not logged in"), 403

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
            create_booking(date=date_arg, id=current_user)

            logging.info(f"Booked date {date_arg} for {current_user}")
            return jsonify(message="Booked"), 200
            
        except Exception as err:
            # Should handle if the date is already booked and any other errors
            logging.error(f"Error booking date {date_arg} for {current_user} "
                          "with error, {err}")
            return jsonify(message="Something went wrong with the request"), 500


@schedule_handler_bp.route("/cancel_booking", methods=["GET"])
def cancel_booking():
    """
    Handler for cancelling the booking on the supplied date if the booker 
    matches the currently logged in user
    """
    date_arg = request.args.get('date')
    current_user = session.get('user_id')

    # Checks if the date can be cancelled first
    if current_user is None:
        logging.debug(f"Date {date_arg} was not cancelled, no user logged in")
        return jsonify(message="Not logged in"), 403
    
    elif datetime.strptime(date_arg, "%Y-%m-%d").date() < date.today():
        logging.debug(f"Date {date_arg} was not cancelled for {current_user} " 
                      "as cancel date is in the past")
        return jsonify(message="Cancel date cannot be in the past"), 403
    
    else:
        try:
            booked_user = get_user_by_date(date_arg)

            # Checks if the date is booked
            if booked_user:
                # Checks if the user on the booking matches the user logged in
                if current_user == booked_user[0]:
                    remove_booking(date_arg)

                    logging.info(f"Cancelled booking by {booked_user[0]} on "
                                 f"{date_arg}")
                    return jsonify(message="Cancelled booking")
                
                else:
                    logging.debug(f"Booking on {date_arg} was not cancelled as "
                                  f"logged in user {current_user} did not match"
                                  f" booked user {booked_user[0]}")
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