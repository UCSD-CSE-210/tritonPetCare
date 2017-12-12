# -*- coding: utf-8 -*-
from Dao import Dao

class PostDao(Dao):
	def init_db(self):
		super(PostDao, self).init_db('posts')

	def get_user_posts(self, userId):
		db = self.get_db()
		respond = db.execute("SELECT * FROM posts WHERE owner_id=:owner_id", {'owner_id': userId})
		return respond.fetchall()

	def check_relation(self, postId, userId):
		db = self.get_db()
		respond = db.execute("SELECT interested, match FROM posts WHERE id=:id", {'id': postId})
		row = respond.fetchone()
		if userId == row['match']:
			return 'MATCHED'
		interestedUsers = [] if row['interested'] is None else str(row['interested']).split(',')
		if userId in interestedUsers:
			return 'INTERESTED'
		return 'UNRELATED'

	def list_all_posts(self, reputation):
		db = self.get_db()
		respond = db.execute("SELECT id, name, species, start_date, end_date, image1, notes FROM posts WHERE criteria<=:reputation", {'reputation': reputation})
		return respond.fetchall()

	def list_limited_posts(self, limit, offset):
		db = self.get_db()
		respond = db.execute("SELECT id, name, species, start_date, end_date, image1, notes FROM posts LIMIT :limit OFFSET :offset;", {'limit': limit, 'offset': offset})
		return respond.fetchall()

	def add_post(self, postInfo):
		db = self.get_db()
		query = ("INSERT INTO posts (name, species, breed, gender, age, vaccination, start_date, end_date, criteria, notes, image1, image2, "
				"image3, owner_id, post_date) VALUES (:name, :species, :breed, :gender, :age, :vaccination, :start_date, :end_date, :criteria, "
				":notes, :image1, :image2, :image3, :owner_id, :post_date)"
		)
		cursor = db.cursor()
		cursor.execute(query, postInfo)
		db.commit()
		return cursor.lastrowid

	def get_post(self, postId):
		db = self.get_db()
		respond = db.execute("SELECT * FROM posts WHERE id=:id", {'id': postId})
		return respond.fetchone()

	def update_post(self, postInfo):
		db = self.get_db()
		query = ("UPDATE posts SET name=:name, species=:species, breed=:breed, gender=:gender, age=:age, vaccination=:vaccination, "
				"start_date=:start_date, end_date=:end_date, criteria=:criteria, notes=:notes, image1=:image1, image2=:image2, "
				"image3=:image3, post_date=:post_date WHERE id=:id"
		)
		db.execute(query, postInfo)
		db.commit()
		return postInfo['id']

	def remove_post(self, postId):
		db = self.get_db()
		respond = db.execute("SELECT image1, image2, image3 FROM posts WHERE id=:id", {'id': postId})
		prevImages = filter(lambda img : img is not None, dict(respond.fetchone()).values())
		db.execute("DELETE FROM posts WHERE id=:id", {'id': postId})
		db.commit()
		return prevImages

	def add_interest(self, postId, userId):
		db = self.get_db()
		respond = db.execute("SELECT interested, match, owner_id FROM posts WHERE id=:id", {'id': postId})
		row = respond.fetchone()
		if row['match'] is not None and len(row['match']) > 0:
			return False
		interestedUsers = [] if row['interested'] is None else str(row['interested']).split(',')
		if userId in interestedUsers:
			return False
		interestedUsers.append(userId)
		db.execute("UPDATE posts SET interested=:interested WHERE id=:id", {'id': postId, 'interested': ','.join(interestedUsers)})
		db.commit()
		return row['owner_id']

	def add_match(self, postId, userId):
		db = self.get_db()
		respond = db.execute("SELECT interested FROM posts WHERE id=:id", {'id': postId})
		row = respond.fetchone()
		interestedUsers = [] if row['interested'] is None else str(row['interested']).split(',')
		if userId not in interestedUsers:
			return False
		db.execute("UPDATE posts SET interested=NULL, match=:match WHERE id=:id", {'id': postId, 'match': userId})
		db.commit()
		return True

	def update_review(self, postId, review):
		db = self.get_db()
		db.execute("UPDATE posts SET review=:review WHERE id=:id", {'id': postId, 'review': review})
		db.commit()
	