DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	species TEXT NOT NULL,
	breed TEXT,
	gender INTEGER NOT NULL,
	age INTEGER NOT NULL,
	vaccination TEXT NOT NULL,
	vaccination_opt TEXT,
	start_date INTEGER NOT NULL,
	end_date INTEGER NOT NULL,
	criteria INTEGER NOT NULL,
	notes TEXT,
	owner_id TEXT NOT NULL,
	post_date INTEGER NOT NULL,
	interested TEXT
);