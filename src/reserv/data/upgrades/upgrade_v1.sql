ALTER TABLE user
ADD status TEXT NOT NULL
DEFAULT "active" CHECK(
	status = "active" OR
	status = "inactive" OR
	status = "terminated"
);

ALTER TABLE user RENAME COLUMN userid to user_id;

ALTER TABLE user RENAME COLUMN displayname to display_name;

ALTER TABLE schedule RENAME COLUMN userid to user_id;

CREATE TABLE IF NOT EXISTS role (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT,
    "desc"  TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS permission (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
    "desc"  TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS role_permission (
	"role_id"	INTEGER NOT NULL,
	"permission_id"	INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS user_role (
	"user_id"	INTEGER NOT NULL,
	"role_id"	INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id)
);

INSERT OR IGNORE INTO role (id, name, desc) VALUES 
(1, "admin", "Can view the schedule and manage all bookings"),
(2, "user", "Can view the schedule and manage their own bookings"),
(3, "guest", "Can only view the schedule");

INSERT OR IGNORE INTO permission (id, name, desc) VALUES 
(1, "manage", "Can make/cancel all bookings to the schedule"),
(2, "book", "Can make/cancel their own bookings to the schedule"),
(3, "view", "Can view the schedule");

INSERT OR IGNORE INTO role_permission (role_id, permission_id) VALUES 
(1, 1), (1, 3),
(2, 2), (2, 3),
(3, 3);

DROP TABLE IF EXISTS archive;