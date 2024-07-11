from .db import get_db

def get_user_by_id(id: str) -> list:
    query = "SELECT * FROM user WHERE userid = ?"
    db = get_db()
    res = db.execute(query, (id,)).fetchone()

    return res

def get_name_by_id(id: str) -> str:
    query = "SELECT displayname FROM user WHERE userid = ?"
    db = get_db()
    res = db.execute(query, (id,)).fetchone()

    return res


def get_user_by_date(date: str) -> str:
    query = "SELECT userid FROM schedule WHERE date = ?"
    db = get_db()
    res = db.execute(query, (date,)).fetchone()

    return res


def update_name(id: str, name: str):
    query = "UPDATE user SET displayname = ? WHERE userid = ? "
    db = get_db()
    db.execute(query, (name, id))
    db.commit()


def update_password(id: str, password: str):
    query = "UPDATE user SET password = ? WHERE userid = ? "
    db = get_db()
    db.execute(query, (password, id))
    db.commit()


def create_booking(date: str, id: str):
    query = "INSERT INTO schedule (date, userid) VALUES (?,?)"
    db = get_db()
    db.execute(query, (date, id))
    db.commit()


def remove_booking(date: str):
    query = "DELETE FROM schedule WHERE date = ?"
    db = get_db()
    db.execute(query, (date,))
    db.commit()


def get_bookings_by_params(date: str, period: str, id: str) -> int:
    query = """
        SELECT COUNT(*)
        FROM schedule
        WHERE strftime('%s', date)
        BETWEEN strftime('%s', ?1)
        AND strftime('%s', DATE(?1, ?2))
        AND userid = ?3
    """

    db = get_db()
    res = db.execute(query, (date, period, id)).fetchone()[0]

    return res