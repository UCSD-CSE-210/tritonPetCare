# -*- coding: utf-8 -*-
import sqlite3
from flask import g, current_app

class Dao(object):
	def get_db(self):
		if not hasattr(g, 'sqlite_db'):
			connection = sqlite3.connect(current_app.config['DATABASE'])
			connection.row_factory = sqlite3.Row
			g.sqlite_db = connection
		return g.sqlite_db

	def close_db(self):
		if hasattr(g, 'sqlite_db'):
			g.sqlite_db.close()

	def init_db(self, table):
		db = self.get_db()
		with current_app.open_resource(table + '.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()