CREATE TABLE "user" (
	"userid"	TEXT NOT NULL UNIQUE,
	"displayname"	TEXT UNIQUE,
	"password"	TEXT,
	PRIMARY KEY("userid")
);

CREATE TABLE "schedule" (
	"date"	TEXT NOT NULL CHECK(date("date") IS NOT NULL) UNIQUE,
	"userid"	TEXT NOT NULL,
	PRIMARY KEY("date")
);

CREATE TABLE "archive" (
	"date"	TEXT NOT NULL CHECK(date("date") IS NOT NULL) UNIQUE,
	"userid"	TEXT,
	PRIMARY KEY("date")
);