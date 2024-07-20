PRAGMA user_version = 1;

CREATE TABLE user (
	"user_id"	TEXT NOT NULL UNIQUE,
	"display_name"	TEXT UNIQUE,
	"password"	TEXT,
	"status"	TEXT NOT NULL DEFAULT "active" CHECK(
		status = "active" OR
		status = "inactive" OR
		status = "terminated"
	),
	PRIMARY KEY("user_id")
);

CREATE TABLE schedule (
	"date"	TEXT NOT NULL CHECK(date("date") IS NOT NULL) UNIQUE,
	"user_id"	TEXT NOT NULL,
	PRIMARY KEY("date")
);