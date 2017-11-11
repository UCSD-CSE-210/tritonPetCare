# -*- coding: utf-8 -*-
import time, datetime
from flask import Blueprint, request, session, redirect, url_for, render_template, abort
from daos import Dao, AccountDao, PostDao

bp = Blueprint('PetCare', __name__)

def init_db():
	AccountDao().init_db()
	PostDao().init_db()

def close_db():
	Dao().close_db()

@bp.route('/', methods=['GET'])
def homepage():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html', error=None)
	accountDao = AccountDao()
	isPasswordCorrect = accountDao.check_account_password(request.form['user'], request.form['password'])
	if isPasswordCorrect is None:
		return render_template('login.html', error="Invalid User Account")
	if not isPasswordCorrect:
		return render_template('login.html', error="Wrong Password")
	session['logged_in'] = request.form['user']
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/logout', methods=['GET'])
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('PetCare.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html', error=None)
	accountDao = AccountDao()
	code = accountDao.add_account(request.form['user'], request.form['password'], request.form['name'])
	if not code:
		return render_template('register.html', error="User Account Existed Already")
	# TODO: send email with authentication url ending with code
	return redirect(url_for('PetCare.login'))

@bp.route('/authenticate', methods=['GET'])
def authenticate():
	accountDao = AccountDao()
	isAuthPass = accountDao.authenticate_account(request.args['user'], request.args['code'])
	if not isAuthPass:
		return render_template('login.html', error="Authentication Failed")
	session['logged_in'] = request.args['user']
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/list_posts', methods=['GET'])
def list_posts():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	reputation = accountDao.get_account_reputation(session['logged_in'])
	postDao = PostDao()
	posts = postDao.list_all_posts(round(reputation))
	[change_time_format(dict(post)) for post in posts]
	return render_template('list_posts.html', posts=posts)

@bp.route('/edit_post', methods=['GET', 'POST'])
def edit_post():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	postDao = PostDao()
	postId = accountDao.get_account_post(session['logged_in'])
	if request.method == 'GET':
		if postId is None:
			return render_template('edit_post.html', error=None)
		post = postDao.get_post(postId)
		# TODO: return with post information shown
		return render_template('edit_post.html', error=None)
	args = make_args(session['logged_in'], request.form)
	if not args:
		return render_template('edit_post.html', error="Required Informaion Missing")
	if postId is None:
		postId = postDao.add_post(args)
		accountDao.update_account_post(session['logged_in'], postId)
	else:
		args['id'] = postId
		postDao.update_post(args)
	return redirect(url_for('PetCare.list_posts'))

def make_args(id, input):
	if not ('name' in input and 'species' in input and 'gender' in input and 'age' in input and 'vaccination'in input and 'start_date'in input and 'end_date' in input and 'criteria' in input):
		return False
	args = input.copy()
	args['owner_id'] = id
	args['start_date'] = int(time.mktime(time.strptime(input['start_date'], '%Y-%m-%d')))
	args['end_date'] = int(time.mktime(time.strptime(input['end_date'], '%Y-%m-%d')))
	args['post_date'] = int(time.time())
	return args

def change_time_format(args):
	args['start_date'] = time.strftime('%Y-%m-%d', time.localtime(args['start_date']))
	args['end_date'] = time.strftime('%Y-%m-%d', time.localtime(args['end_date']))
	if 'post_date' in args:
		args['post_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(args['post_date']))

