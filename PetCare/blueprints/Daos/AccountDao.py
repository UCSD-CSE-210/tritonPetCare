# -*- coding: utf-8 -*-
import uuid
from Dao import Dao

class AccountDao(Dao):
	def init_db(self):
		super(AccountDao, self).init_db('accounts')

	def check_account_password(self, id, password):
		db = self.get_db()
		respond = db.execute("SELECT password FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		if row is None:
			return None
		return row['password'] == password

	def add_account(self, id, password, name, gender, age, department = None, college = None):
		db = self.get_db()
		respond = db.execute("SELECT verified FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		code = str(uuid.uuid4())
		if row is None:
			db.execute("INSERT INTO accounts (id, password, name, gender, age, department, college, reputation_sum, reputation_num, verified, code) VALUES (:id, :password, :name, :gender, :age, :department, :college, 8, 2, 0, :code)",
					{'id': id, 'password': password, 'name': name, 'gender': gender, 'age': age, 'department': department, 'college':college, 'code': code})
			db.commit()
			return code
		if row['verified'] == 0:
			db.execute("UPDATE accounts SET password=:password, name=:name, gender=:gender, age=:age, department=:department, college=:college, code=:code WHERE id=:id",
					{'id': id, 'password': password, 'name': name, 'gender': gender, 'age': age, 'department': department, 'college':college, 'code': code})
			db.commit()
			return code
		return False

	def authenticate_account(self, id, code):
		db = self.get_db()
		respond = db.execute("SELECT code FROM accounts WHERE id=:id AND verified=0", {'id': id})
		row = respond.fetchone()
		if row is None or code != row['code']:
			return False
		db.execute("UPDATE accounts SET verified=1, code=NULL WHERE id=:id", {'id': id})
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

	def get_account_all_info(self, id):
		db = self.get_db()
		respond = db.execute("SELECT * FROM accounts WHERE id=:id", {'id': id})
		row = respond.fetchone()
		return row

	def remove_account_post(self, id, postId):
		db = self.get_db()
		respond = db.execute("SELECT current_post FROM accounts WHERE id=:id", {'id': id})
		if int(postId) != respond.fetchone()['current_post']:
			return False
		db.execute("UPDATE accounts SET current_post=NULL WHERE id=:id", {'id': id})
		db.commit()
		return True
