CREATE TABLE user_new (
	"user_id" TEXT NOT NULL UNIQUE,
    "created_on" TEXT NOT NULL CHECK(date("created_on")) DEFAULT (
        strftime('%Y-%m-%d %H:%M:%S', 'now')
    ),
    "updated_on" TEXT NOT NULL CHECK(date("updated_on")) DEFAULT (
        strftime('%Y-%m-%d %H:%M:%S', 'now')
    ),
	"display_name" TEXT UNIQUE,
	"password" TEXT,
	"status" TEXT NOT NULL DEFAULT "active" CHECK(
		status = "active" OR
		status = "inactive" OR
		status = "terminated"
	),
	PRIMARY KEY("user_id")
);

INSERT INTO user_new(user_id, display_name, password, status) SELECT * FROM user;

DROP TABLE user;
ALTER TABLE user_new RENAME TO user;

CREATE TRIGGER user_updated_on_update
    BEFORE UPDATE ON user
BEGIN
    UPDATE user
    SET updated_on = strftime('%Y-%m-%d %H:%M:%S', 'now') 
    WHERE user_id = old.user_id;
END;

CREATE TRIGGER user_created_on_immutable
    BEFORE UPDATE OF created_on ON user
BEGIN
    SELECT RAISE(FAIL, "Created on is read only");
END;