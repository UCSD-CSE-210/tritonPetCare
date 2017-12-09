DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
	id TEXT PRIMARY KEY,
	email TEXT NOT NULL,
	password TEXT NOT NULL,
	name TEXT NOT NULL,
	gender INTEGER NOT NULL,
	age INTEGER NOT NULL,
	department TEXT NOT NULL,
	college TEXT,
	reputation_sum INTEGER NOT NULL,
	reputation_num INTEGER NOT NULL,
	verified INTEGER NOT NULL,
	code TEXT,
	current_post INTEGER
);