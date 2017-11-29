# -*- coding: utf-8 -*-
from Dao import Dao

class PostDao(Dao):
	def init_db(self):
		super(PostDao, self).init_db('posts')

	def list_all_posts(self, reputation):
		db = self.get_db()
		respond = db.execute("SELECT id, name, species, start_date, end_date FROM posts WHERE criteria<=:reputation", {'reputation': reputation})
		return respond.fetchall()

	def get_post(self, id):
		db = self.get_db()
		respond = db.execute("SELECT * FROM posts WHERE id=:id", {'id': id})
		return respond.fetchone()

	def get_user_post(self, user_id):
		db = self.get_db()
		respond = db.execute("SELECT * FROM posts WHERE owner_id=:id", {'id': user_id})
		return respond.fetchall()

	def add_post(self, postInfo):
		db = self.get_db()
		query = ("INSERT INTO posts (name, species, breed, gender, age, vaccination, vaccination_opt, start_date, end_date, criteria, notes, "
				"owner_id, post_date) VALUES (:name, :species, :breed, :gender, :age, :vaccination, :vaccination_opt, :start_date, :end_date, "
				":criteria, :notes, :owner_id, :post_date)"
		)
		cursor = db.cursor()
		cursor.execute(query, postInfo)
		db.commit()
		return cursor.lastrowid

	def update_post(self, postInfo):
		db = self.get_db()
		query = ("UPDATE posts SET name=:name, species=:species, breed=:breed, gender=:gender, age=:age, vaccination=:vaccination, "
				"vaccination_opt=:vaccination_opt, start_date=:start_date, end_date=:end_date, criteria=:criteria, notes=:notes, "
				"post_date=:post_date WHERE id=:id"
		)
		db.execute(query, postInfo)
		db.commit()
		return id

	def remove_post(self, id):
		db = self.get_db()
		db.execute("DELETE FROM posts WHERE id=:id", {'id': id})
		db.commit()

	def add_interest(self, id, user):
		db = self.get_db()
		respond = db.execute("SELECT interested FROM posts WHERE id=:id", {'id': id})
		interestedUsers = [] if respond.fetchone()['interested'] is None else str(respond.fetchone()['interested']).split(',')
		if user in interestedUsers:
			return False;
		interestedUsers.append(user)
		db.execute("UPDATE posts SET interested=:interested WHERE id=:id", {'id': id, 'interested': ','.join(interestedUsers)})
		db.commit()
		return True
	