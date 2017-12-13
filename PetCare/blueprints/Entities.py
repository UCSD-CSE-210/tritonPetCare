# -*- coding: utf-8 -*-
import time, datetime, uuid
from ImageHandler import ImageHandler

class Entities(object):
	@staticmethod
	def make_account_info(input):
		accountInfo = input.form.copy()
		if not Entities.attrNotNull(accountInfo, ['email', 'password', 'name', 'gender', 'age', 'department']):
			return False
		if not Entities.attrNotZeroLength(accountInfo, ['email', 'password', 'name', 'department']):
			return False
		accountInfo['id'] = ''.join(str(uuid.uuid4()).split('-'))[:10]
		accountInfo['code'] = str(uuid.uuid4())
		return accountInfo

	@staticmethod
	def make_post_info(userId, input, prevPost=None):
		postInfo = input.form.copy()
		if not Entities.attrNotNull(postInfo, ['name', 'species', 'gender', 'age', 'vaccination', 'start_date', 'end_date', 'criteria']):
			return False
		if not Entities.attrNotZeroLength(postInfo, ['name', 'species', 'vaccination']):
			return False
		postInfo['owner_id'] = userId
		postInfo['start_date'] = int(time.mktime(time.strptime(postInfo['start_date'], '%Y-%m-%d')))
		postInfo['end_date'] = int(time.mktime(time.strptime(postInfo['end_date'], '%Y-%m-%d')))
		postInfo['post_date'] = int(time.time())
		for i in ['image1', 'image2', 'image3']:		# FIXME: what strategy to be used for uploading pictures
			if i in input.files and input.files[i] is not None and len(input.files[i].filename) > 0:
				postInfo[i] = ImageHandler.save_image(input.files[i])
				if prevPost is not None and i in prevPost:
					ImageHandler.delete_image(prevPost[i])
		return postInfo

	@staticmethod
	def make_post_output(postInfo):
		postInfo['start_date_year_first'] = time.strftime('%Y-%m-%d', time.localtime(postInfo['start_date']))
		postInfo['end_date_year_first'] = time.strftime('%Y-%m-%d', time.localtime(postInfo['end_date']))
		
		postInfo['start_date'] = time.strftime('%m/%d/%Y', time.localtime(postInfo['start_date']))
		postInfo['end_date'] = time.strftime('%m/%d/%Y', time.localtime(postInfo['end_date']))
		if 'post_date' in postInfo:
			postInfo['post_date'] = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(postInfo['post_date']))
		if 'gender' in postInfo:
			postInfo['gender'] = 'Male' if postInfo['gender'] == 1 else 'Female'
		if 'age' in postInfo:
			postInfo['age'] = '<1 year' if postInfo['age'] == 0 else '>= 10 years' if postInfo['age'] == 10 else (str(postInfo['age']) + ' years')
		if 'interested' in postInfo:
			postInfo['interested'] = [] if postInfo['interested'] is None else postInfo['interested'].split(',')
		for i in ['image1', 'image2', 'image3']:
			if i in postInfo and postInfo[i] is not None:
				postInfo[i] = ImageHandler.get_image_full_path(postInfo[i])
		return postInfo

	@staticmethod
	def attrNotNull(info, attrs):
		for attr in attrs:
			if attr not in info:
				return False
		return True

	@staticmethod
	def attrNotZeroLength(info, attrs):
		for attr in attrs:
			if len(info[attr]) == 0:
				return False
		return True