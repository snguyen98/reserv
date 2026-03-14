CREATE TABLE availability (
    "date"	TEXT NOT NULL CHECK(date("date") IS NOT NULL),
    "created_on" TEXT NOT NULL CHECK(date("created_on")) DEFAULT (
        strftime('%Y-%m-%d %H:%M:%S', 'now')
    ),
    "updated_on" TEXT NOT NULL CHECK(date("updated_on")) DEFAULT (
        strftime('%Y-%m-%d %H:%M:%S', 'now')
    ),
	"user_id" TEXT NOT NULL,
	"status" TEXT NOT NULL DEFAULT "unavailable" CHECK(
        status = "available" OR
        status = "unavailable"
    ),
	PRIMARY KEY(date, user_id)
);