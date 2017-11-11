DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
	id TEXT PRIMARY KEY,
	password TEXT NOT NULL,
	name TEXT NOT NULL,
	reputation_sum INTEGER NOT NULL,
	reputation_num INTEGER NOT NULL,
	verified INTEGER NOT NULL,
	code TEXT NOT NULL,
	current_post INTEGER
);