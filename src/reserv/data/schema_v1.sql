PRAGMA user_version = 1;

CREATE TABLE user (
	"userid"	TEXT NOT NULL UNIQUE,
	"displayname"	TEXT UNIQUE,
	"password"	TEXT,
	"status"	TEXT NOT NULL DEFAULT "active" CHECK(
		status = "active" OR
		status = "inactive" OR
		status = "terminated"
	),
	PRIMARY KEY("userid")
);

CREATE TABLE schedule (
	"date"	TEXT NOT NULL CHECK(date("date") IS NOT NULL) UNIQUE,
	"userid"	TEXT NOT NULL,
	PRIMARY KEY("date")
);