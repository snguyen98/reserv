from .db import get_db

def get_user_by_id(id: str) -> list:
    query = "SELECT * FROM user WHERE user_id = ?"
    db = get_db()
    res = db.execute(query, (id,)).fetchone()

    return res

def get_name_by_id(id: str) -> str:
    query = "SELECT display_name FROM user WHERE user_id = ?"
    db = get_db()
    res = db.execute(query, (id,)).fetchone()

    return res


def get_booking_by_date(date: str) -> str:
    query = "SELECT user_id, status FROM schedule WHERE date = ?"
    db = get_db()
    res = db.execute(query, (date,)).fetchone()

    return res


def update_name(id: str, name: str):
    query = "UPDATE user SET display_name = ? WHERE user_id = ? "
    db = get_db()
    db.execute(query, (name, id))
    db.commit()


def update_password(id: str, password: str):
    query = "UPDATE user SET password = ? WHERE user_id = ? "
    db = get_db()
    db.execute(query, (password, id))
    db.commit()


def create_booking(date: str, id: str):
    query = "INSERT INTO schedule (date, user_id) VALUES (?,?)"
    db = get_db()
    db.execute(query, (date, id))
    db.commit()


def update_booking(date: str, id: str):
    query = """
        UPDATE schedule SET
        status = 'booked',
        user_id = ?1
        WHERE date = ?2
    """
    db = get_db()
    db.execute(query, (id, date,))
    db.commit()


def remove_booking(date: str):
    query = "UPDATE schedule SET status = 'cancelled' WHERE date = ?"
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
        AND user_id = ?3
        AND status = 'booked'
    """

    db = get_db()
    res = db.execute(query, (date, period, id)).fetchone()[0]

    return res


def get_user_status(id: str) -> str:
    query = "SELECT status FROM user WHERE user_id = ?"

    db = get_db()
    res = db.execute(query, (id,)).fetchone()[0]

    return res


def get_user_roles(id: str) -> list:
    query = "SELECT role_id FROM user_role WHERE user_id = ?"

    db = get_db()
    res = db.execute(query, (id,)).fetchall()

    return res


def get_user_permissions(id: str) -> set:
    roles = get_user_roles(id)

    perms = set()

    for role_id in roles:
        query = "SELECT permission_id FROM role_permission WHERE role_id = ?"

        db = get_db()
        res = db.execute(query, (role_id[0],)).fetchall()

        role_perms = [perm[0] for perm in res]
        perms.update(role_perms)

    return perms


def get_perm_by_name(name: str) -> int:
    query = "SELECT id FROM permission WHERE name = ?"

    db = get_db()
    res = db.execute(query, (name,)).fetchone()[0]

    return res


def check_perm(id: str, perm: str) -> bool:
    """
    Checks if the user with the supplied id has the supplied permission (name)
    and returns True if so, otherwise False

    Params
    ------
    user_id     The id of the user to check the permissions
    perm        The name (not id) of the permission to check
    """
    perms = get_user_permissions(id)

    return get_perm_by_name(perm) in perms