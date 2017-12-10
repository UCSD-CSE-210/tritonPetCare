# -*- coding: utf-8 -*-
from Dao import Dao

class AccountDao(Dao):
	def init_db(self):
		super(AccountDao, self).init_db('accounts')

	def add_account(self, accountInfo):
		db = self.get_db()
		respond = db.execute("SELECT verified FROM accounts WHERE email=:email", {'email': accountInfo['email']})
		row = respond.fetchone()
		if row is not None and row['verified'] == 1:
			return False
		if row is None:
			query = ("INSERT INTO accounts (id, email, password, name, gender, age, department, college, reputation_sum, reputation_num, verified, code) "
					"VALUES (:id, :email, :password, :name, :gender, :age, :department, :college, 8, 2, 0, :code)"
			)
		else:
			query = ("UPDATE accounts SET id=:id, password=:password, name=:name, gender=:gender, age=:age, department=:department, college=:college, "
					"code=:code WHERE email=:email"
			)
		db.execute(query, accountInfo)
		db.commit()
		return True

	def authenticate_account(self, userId, code):
		db = self.get_db()
		respond = db.execute("SELECT code FROM accounts WHERE id=:id AND verified=0", {'id': userId})
		row = respond.fetchone()
		if row is None or code != row['code']:
			return False
		db.execute("UPDATE accounts SET verified=1, code=NULL WHERE id=:id", {'id': userId})
		db.commit()
		return True

	def check_account_email_password(self, email, password):
		db = self.get_db()
		respond = db.execute("SELECT id, password FROM accounts WHERE email=:email", {'email': email})
		row = respond.fetchone()
		if row is None:
			return None
		if row['password'] != password:
			return False
		return row['id']

	def get_account_info(self, userId):
		db = self.get_db()
		respond = db.execute("SELECT * FROM accounts WHERE id=:id", {'id': userId})
		return respond.fetchone()

	def get_account_reputation(self, userId):
		db = self.get_db()
		respond = db.execute("SELECT reputation_sum, reputation_num FROM accounts WHERE id=:id", {'id': userId})
		row = respond.fetchone()
		return row['reputation_sum'] * 1.0 / row['reputation_num']

	def get_account_post(self, userId):
		db = self.get_db()
		respond = db.execute("SELECT current_post FROM accounts WHERE id=:id", {'id': userId})
		return respond.fetchone()['current_post']

	def update_account_post(self, userId, postId):
		db = self.get_db()
		db.execute("UPDATE accounts SET current_post=:current_post WHERE id=:id", {'id': userId, 'current_post': postId})
		db.commit()

	def remove_account_post(self, userId, postId):
		db = self.get_db()
		respond = db.execute("SELECT current_post FROM accounts WHERE id=:id", {'id': userId})
		if int(postId) != respond.fetchone()['current_post']:
			return False
		db.execute("UPDATE accounts SET current_post=NULL WHERE id=:id", {'id': userId})
		db.commit()
		return True

	def check_account_id_password(self, userId, password):
		db = self.get_db()
		respond = db.execute("SELECT password FROM accounts WHERE id=:id", {'id': userId})
		row = respond.fetchone()
		if row is None:
			return None
		return row['password'] == password

	def update_account_reputation(self, id, score):
		db = self.get_db()
		respond = db.execute("SELECT reputation_sum, reputation_num FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		db.execute("UPDATE accounts SET reputation_sum=:reputation_sum, reputation_num=:reputation_num WHERE id=:id",
					{'id': id, 'reputation_sum': row['reputation_sum'] + score, 'reputation_num': reputation_num + 1})
		db.commit()
