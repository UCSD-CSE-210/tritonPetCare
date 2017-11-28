# -*- coding: utf-8 -*-
import time, datetime
from flask import Blueprint, request, session, redirect, url_for, render_template, abort
from Daos.Dao import Dao
from Daos.AccountDao import AccountDao
from Daos.PostDao import PostDao

bp = Blueprint('PetCare', __name__)

def init_db():
	AccountDao().init_db()
	PostDao().init_db()

def close_db():
	Dao().close_db()

@bp.route('/', methods=['GET'])
def homepage():
	# if session.get('logged_in') is None:
	# 	return redirect(url_for('PetCare.login'))
	# return redirect(url_for('PetCare.list_posts'))
	return render_template('home_page.html')

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
	return redirect(url_for('PetCare.homepage'))

@bp.route('/logout', methods=['GET'])
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('PetCare.homepage'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html', error=None)
	accountDao = AccountDao()
	code = accountDao.add_account(request.form['user'], request.form['password'], request.form['name'], request.form['gender'], request.form['age'], request.form['department'], request.form['college'])
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

@bp.route('/profile', methods=['GET'])
def profile():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	info = accountDao.get_account_all_info(session['logged_in'])
	postDao = PostDao()
	posts = postDao.list_all_posts(round(reputation))
	[change_time_format(dict(post)) for post in posts]
	return render_template('profile.html', posts=posts)


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
	postInfo = make_post_info(session['logged_in'], request.form)
	if not postInfo:
		return render_template('edit_post.html', error="Required Informaion Missing")
	if postId is None:
		postId = postDao.add_post(postInfo)
		accountDao.update_account_post(session['logged_in'], postId)
	else:
		postInfo['id'] = postId
		postDao.update_post(postInfo)
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/view_post', methods=['GET'])
def view_post():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	postDao = PostDao()
	post = postDao.get_post(request.args['id'])
	change_time_format(dict(post))
	return render_template('view_post.html', post=post)

@bp.route('/delete_post', methods=['POST'])
def delete_post():
	if session.get('logged_in') is not None:
		accountDao = AccountDao()
		ownerMatched = accountDao.remove_account_post(session['logged_in'], request.form['id'])
		if not ownerMatched:
			return redirect(url_for('PetCare.list_posts'))
		postDao = PostDao()
		postDao.remove_post(request.form['id'])
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/interest_post', methods=['POST'])
def interest_post():
	if session.get('logged_in') is not None:
		postDao = PostDao()
		firstTimeInteresting = postDao.add_interest(request.form['id'], session['logged_in'])
		# if firstTimeInteresting:
		# 	sendEmail()
	return redirect(url_for('PetCare.list_posts'))

def make_post_info(id, input):
	postInfo = input.copy()
	if not ('name' in postInfo and 'species' in postInfo and 'gender' in postInfo and 'age' in postInfo and 'vaccination'in postInfo
			and 'start_date'in postInfo and 'end_date' in postInfo and 'criteria' in postInfo):
		return False
	postInfo['owner_id'] = id
	postInfo['start_date'] = int(time.mktime(time.strptime(postInfo['start_date'], '%Y-%m-%d')))
	postInfo['end_date'] = int(time.mktime(time.strptime(postInfo['end_date'], '%Y-%m-%d')))
	postInfo['post_date'] = int(time.time())
	return postInfo

def change_time_format(postInfo):
	postInfo['start_date'] = time.strftime('%Y-%m-%d', time.localtime(postInfo['start_date']))
	postInfo['end_date'] = time.strftime('%Y-%m-%d', time.localtime(postInfo['end_date']))
	if 'post_date' in postInfo:
		postInfo['post_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(postInfo['post_date']))

