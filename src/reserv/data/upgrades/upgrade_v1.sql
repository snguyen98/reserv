ALTER TABLE user
ADD status TEXT NOT NULL
DEFAULT "active" CHECK(
	status = "active" OR
	status = "inactive" OR
	status = "terminated"
);