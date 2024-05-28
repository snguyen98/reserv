from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash

from ..data.db import get_db

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

    if session.get("user_id") is not None:
        db.execute("INSERT INTO schedule (date, userid) VALUES (?,?)", (date_arg, session.get("user_id")))
        db.commit()

        return jsonify(success=True)
    else:
        return jsonify(success=False)


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


@schedule_bp.route("/set_password")
def set_password():
    user_id = "Chungus"
    password = "test"
    hash_password = generate_password_hash(password)
    
    db = get_db()
    db.execute("UPDATE user SET password = ? WHERE userid = ?", (hash_password, user_id))
    db.commit()