DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	species TEXT NOT NULL,
	breed TEXT,
	gender INTEGER NOT NULL,
	age INTEGER NOT NULL,
	vaccination TEXT NOT NULL,
	start_date INTEGER NOT NULL,
	end_date INTEGER NOT NULL,
	criteria INTEGER NOT NULL,
	notes TEXT,
	image1 TEXT NOT NULL,
	image2 TEXT,
	image3 TEXT,
	owner_id TEXT NOT NULL,
	post_date INTEGER NOT NULL,
	interested TEXT,
	match TEXT,
	review INTEGER
);