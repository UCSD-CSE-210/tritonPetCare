# -*- coding: utf-8 -*-
import os
import sqlite3
import uuid
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

class AccountDao(Dao):
	def init_db(self):
		super(AccountDao, self).init_db('accounts')

	def check_account_password(self, id, password):
		db = self.get_db()
		respond = db.execute("SELECT password FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone();
		if row is None:
			return None
		return row['password'] == password

	def add_account(self, id, password, name):
		db = self.get_db()
		respond = db.execute("SELECT verified FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		code = str(uuid.uuid4())
		if row is None:
			db.execute("INSERT INTO accounts (id, password, name, reputation_sum, reputation_num, verified, code) VALUES (:id, :password, :name, 8, 2, 0, :code)",
					{'id': id, 'password': password, 'name': name, 'code': code})
			db.commit()
			return code
		if row['verified'] == 0:
			db.execute("UPDATE accounts SET password=:password, name=:name, code=:code WHERE id=:id",
					{'id': id, 'password': password, 'name': name, 'code': code})
			db.commit()
			return code
		return False

	def authenticate_account(self, id, code):
		db = self.get_db()
		respond = db.execute("SELECT code FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		if row is None or code != row['code']:
			return False
		code = str(uuid.uuid4())
		db.execute("UPDATE accounts SET verified=1, code=:code WHERE id=:id", {'id': id, "code": code})
		db.commit()
		return True

	def get_account_post(self, id):
		db = self.get_db()
		respond = db.execute("SELECT current_post FROM accounts WHERE id=:id", {'id': id})
		return respond.fetchone()['current_post']

	def update_account_post(self, id, post):
		db = self.get_db()
		db.execute("UPDATE accounts SET current_post=:current_post WHERE id=:id", {'id': id, 'current_post': post})
		db.commit()

	def get_account_reputation(self, id):
		db = self.get_db()
		respond = db.execute("SELECT reputation_sum, reputation_num FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		return row['reputation_sum'] * 1.0 / row['reputation_num']

	def update_account_reputation(self, id, score):
		db = self.get_db()
		respond = db.execute("SELECT reputation_sum, reputation_num FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		db.execute("UPDATE accounts SET reputation_sum=:reputation_sum, reputation_num=:reputation_num WHERE id=:id",
					{'id': id, 'reputation_sum': row['reputation_sum'] + score, 'reputation_num': reputation_num + 1})
		db.commit()

class PostDao(Dao):
	def init_db(self):
		super(PostDao, self).init_db('posts')

	def list_all_posts(self, reputation):
		db = self.get_db()
		respond = db.execute("SELECT id, name, species, start_date, end_date FROM posts WHERE criteria<=:reputation", {'reputation': reputation})
		return respond.fetchall();

	def get_post(self, id):
		db = self.get_db()
		respond = db.execute("SELECT * FROM posts WHERE id=:id", {'id': id})
		return respond.fetchone();

	def add_post(self, args):
		db = self.get_db()
		query = ("INSERT INTO posts (name, species, breed, gender, age, vaccination, vaccination_opt, start_date, end_date, criteria, notes, "
				"owner_id, post_date) VALUES (:name, :species, :breed, :gender, :age, :vaccination, :vaccination_opt, :start_date, :end_date, "
				":criteria, :notes, :owner_id, :post_date)"
		)
		cursor = db.cursor()
		cursor.execute(query, args)
		db.commit()
		return cursor.lastrowid

	def update_post(self, args):
		db = self.get_db()
		query = ("UPDATE posts SET name=:name, species=:species, breed=:breed, gender=:gender, age=:age, vaccination=:vaccination, "
				"vaccination_opt=:vaccination_opt, start_date=:start_date, end_date=:end_date, criteria=:criteria, notes=:notes, "
				"post_date=:post_date WHERE id=:id"
		)
		db.execute(query, args)
		db.commit()
		return id

	def remove_post(self, id):
		db = self.get_db()
		db.execute("DELETE FROM posts WHERE id=:id", {'id': id})
		db.commit()

	