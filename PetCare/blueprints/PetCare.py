# -*- coding: utf-8 -*-
from flask import Blueprint, request, session, redirect, url_for, render_template, abort, jsonify
import time
from Daos.Dao import Dao
from Daos.AccountDao import AccountDao
from Daos.PostDao import PostDao
from ImageHandler import ImageHandler
from Entities import Entities
from EmailHandler import EmailHandler

bp = Blueprint('PetCare', __name__)

def init_db():
	AccountDao().init_db()
	PostDao().init_db()

def close_db():
	Dao().close_db()

@bp.route('/', methods=['GET'])
def homepage():
	return render_template('home_page.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html', error=None)
	accountInfo = Entities.make_account_info(request)
	if not accountInfo:
		return render_template('register.html', error="Required Informaion Missing")
	accountDao = AccountDao()
	isNewAccount = accountDao.add_account(accountInfo)
	if not isNewAccount:
		return render_template('register.html', error="User Account Existed Already")
	EmailHandler.send_authentication(accountInfo['email'], accountInfo['id'], accountInfo['code'])
	return redirect(url_for('PetCare.login'))

@bp.route('/authenticate', methods=['GET'])
def authenticate():
	accountDao = AccountDao()
	isAuthPass = accountDao.authenticate_account(request.args['userId'].rstrip(), request.args['code'])
	if not isAuthPass:
		return render_template('login.html', error="Authentication Failed")
	session['logged_in'] = request.args['userId'].rstrip()
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html', error=None)
	accountDao = AccountDao()
	userId = accountDao.check_account_email_password(request.form['email'], request.form['password'])
	if userId is None:
		return render_template('login.html', error="Invalid User Account")
	if not userId:
		return render_template('login.html', error="Wrong Password")
	session['logged_in'] = userId
	return redirect(url_for('PetCare.homepage'))

@bp.route('/logout', methods=['GET'])
def logout():
	session.pop('logged_in', None)
	return redirect(url_for('PetCare.login'))

@bp.route('/profile', methods=['GET'])
def profile():
	if 'login' in request.args and session.get('logged_in') is not None and session.get('logged_in') != request.args['login']:
		session.pop('logged_in', None)
	if session.get('logged_in') is None:
		if 'login' not in request.args:
			return redirect(url_for('PetCare.login')) 
		else:
			return redirect(url_for('PetCare.prompt_login', userId=request.args['login'], targetId=request.args['userId'].rstrip()))
	accountDao = AccountDao()
	postDao = PostDao()
	accountInfo = accountDao.get_account_info(request.args['userId'].rstrip())
	posts = postDao.get_user_posts(request.args['userId'].rstrip())
	postInfos = [Entities.make_post_output(dict(post)) for post in posts]
	myCurrentPostId = accountDao.get_account_post(session['logged_in'].rstrip())
	status = 'UNRELATED' if myCurrentPostId is None else postDao.check_relation(myCurrentPostId, request.args['userId'].rstrip())
	return render_template('profile.html', account=accountInfo, posts=postInfos, status=status)

@bp.route('/list_posts', methods=['GET'])
def list_posts():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	reputation = accountDao.get_account_reputation(session['logged_in'].rstrip())		
	postDao = PostDao()
	posts = postDao.list_limited_posts(reputation=reputation, limit=4, offset=0)
	postInfos = [Entities.make_post_output(dict(post)) for post in posts]
	return render_template('list_posts.html', posts=postInfos, fromFilter=False)

@bp.route('/_load_more_posts', methods=['GET'])
def load_more_posts():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	reputation = accountDao.get_account_reputation(session['logged_in'].rstrip())
	postDao = PostDao()
	posts = postDao.list_limited_posts(reputation=reputation, limit=4, offset=request.args.get('offset'))
	postInfos = [Entities.make_post_output(dict(post)) for post in posts]
	return jsonify(postInfos)

@bp.route('/filter_posts', methods=['POST'])
def filter_posts():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))

	gender_filter = request.form['gender']
	species_filter = request.form['species']
	age_filter = request.form['age']

	start_date = request.form['start_date']
	end_date = request.form['end_date']
	start_date_value = int(time.mktime(time.strptime(start_date, '%Y-%m-%d'))) if len(start_date) > 0 else 0
	end_date_value = int(time.mktime(time.strptime(end_date, '%Y-%m-%d'))) if len(end_date) > 0 else 0

	accountDao = AccountDao()
	reputation = accountDao.get_account_reputation(session['logged_in'])
	postDao = PostDao()
	all_posts = postDao.list_all_posts(reputation=reputation)

	filtered_posts = []
	for post in all_posts:
		if gender_filter != '-1' and int(gender_filter) != post['gender']:
			continue
		if len(species_filter) > 0 and species_filter != post['species']:
			continue
		if age_filter != '-1' and int(age_filter) != post['age']:
			continue
		if len(start_date) > 0 and post['start_date'] < start_date_value:
			continue
		if len(end_date) > 0 and post['end_date'] > end_date_value:
			continue			
		filtered_posts.append(post)

	postInfos = [Entities.make_post_output(dict(post)) for post in filtered_posts]
	return render_template('list_posts.html', posts=postInfos, fromFilter=True)

@bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	postDao = PostDao()
	postId = accountDao.get_account_post(session['logged_in'].rstrip())
	if postId is not None:
		return redirect(url_for('PetCare.edit_post'))
	if request.method == 'GET':
		return render_template('create_post.html', error=None)
	postInfo = Entities.make_post_info(session['logged_in'].rstrip(), request)
	if not postInfo:
		return render_template('create_post.html', error="Required Informaion Missing")
	postId = postDao.add_post(postInfo)
	accountDao.update_account_post(session['logged_in'].rstrip(), postId)
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/edit_post', methods=['GET', 'POST'])
def edit_post():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	postDao = PostDao()	
	postId = accountDao.get_account_post(session['logged_in'].rstrip())
	
	if postId is None:
		return redirect(url_for('PetCare.create_post'))
	
	prevPost = postDao.get_post(postId)
	prevPostInfo = Entities.make_post_output(dict(prevPost))
	if request.method == 'GET':
		return render_template('edit_post.html', error=None, prevPost=prevPostInfo)

	prevPostDict = dict(prevPost)
	postInfo = Entities.make_post_info(session['logged_in'].rstrip(), request, prevPostDict)
	if not postInfo:
		return render_template('edit_post.html', error="Required Informaion Missing", prevPost=None)
	
	postInfo['id'] = postId
	postDao.update_post(postInfo)
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/view_post', methods=['GET'])
def view_post():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	postDao = PostDao()
	post = postDao.get_post(request.args['postId'])
	status = 'PENDING'
	if post['match'] is not None and len(post['match']) > 0:
		status = 'MATCHED'
	if time.time() > post['end_date']:
		status = 'FINISHED'
	postInfo = Entities.make_post_output(dict(post))
	isOwner = (session.get('logged_in') == post['owner_id'])
	accountDao = AccountDao()
	ownername =  accountDao.get_name(post['owner_id'])
	return render_template('view_post.html', post=postInfo, status=status, isOwner=isOwner, owner=ownername)

@bp.route('/delete_post', methods=['POST'])
def delete_post():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	ownerMatched = accountDao.remove_account_post(session['logged_in'].rstrip(), request.form['postId'])
	if not ownerMatched:
		return redirect(url_for('PetCare.list_posts'))
	postDao = PostDao()
	prevImages = postDao.remove_post(request.form['postId'])
	for img in prevImages:
		ImageHandler.delete_image(img)
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/interest_post', methods=['POST'])
def interest_post():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	postDao = PostDao()
	postOwnerId = postDao.add_interest(request.form['postId'], session['logged_in'].rstrip())
	if postOwnerId:
		postOwnerEmail = accountDao.get_account_email(postOwnerId)
		userEmail = accountDao.get_account_email(session['logged_in'].rstrip())
		EmailHandler.send_interest(postOwnerId, postOwnerEmail, session['logged_in'].rstrip(), userEmail)
	return redirect(url_for('PetCare.list_posts'))

@bp.route('/prompt_login', methods=['GET', 'POST'])
def prompt_login():
	if request.method == 'GET':
		return render_template('prompt_login.html', userId=request.args['userId'].rstrip(), targetId=request.args['targetId'], error=None)
	accountDao = AccountDao()
	if not accountDao.check_account_id_password(request.form['userId'], request.form['password']):
		return render_template('prompt_login.html', userId=request.form['userId'], targetId=request.form['targetId'], error="Wrong Password")
	session['logged_in'] = request.form['userId']
	return redirect(url_for('PetCare.profile', userId=request.form['targetId']))

@bp.route('/match', methods=['POST'])
def match():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	postId = accountDao.get_account_post(session['logged_in'].rstrip())
	if postId is not None:
		postDao = PostDao()
		if postDao.add_match(postId, request.form['userId']):
			careGiverEmail = accountDao.get_account_email(request.form['userId'])
			userEmail = accountDao.get_account_email(session['logged_in'].rstrip())
			EmailHandler.send_approval(careGiverEmail, postId, userEmail)
	return redirect(url_for('PetCare.profile', userId=request.form['userId']))

@bp.route('/review', methods=['POST'])
def review():
	if session.get('logged_in') is None:
		return redirect(url_for('PetCare.login'))
	accountDao = AccountDao()
	postId = accountDao.get_account_post(session['logged_in'].rstrip())
	if postId is not None:
		postDao = PostDao()
		post = postDao.get_post(postId)
		if post['match'] is not None:
			postDao.update_review(post['id'], int(request.form['review']))
			accountDao.update_account_reputation(post['match'], int(request.form['review']), post['review'])
			if time.time() > post['end_date']:
				accountDao.remove_account_post(session['logged_in'].rstrip(), post['id'])
			return redirect(url_for('PetCare.profile', userId=post['match']))
	return redirect(url_for('PetCare.list_posts'))
