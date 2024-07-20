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