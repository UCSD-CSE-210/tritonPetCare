DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
	id TEXT PRIMARY KEY,
	password TEXT NOT NULL,
	name TEXT NOT NULL,
	gender TEXT NOT NULL,
	age INTEGER NOT NULL,
	reputation_sum INTEGER NOT NULL,
	reputation_num INTEGER NOT NULL,
	verified INTEGER NOT NULL,
	code TEXT,
	current_post INTEGER
);