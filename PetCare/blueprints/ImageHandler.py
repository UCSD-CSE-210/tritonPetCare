# -*- coding: utf-8 -*-
import os, uuid
from flask import current_app

class ImageHandler(object):
	@staticmethod
	def save_image(file):
		filename = ''.join(str(uuid.uuid4()).split('-')) + '.' + file.filename.split('.')[-1]
		file.save(os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], filename))
		return filename

	@staticmethod
	def get_image_full_path(filename):
		return "../static/images/" + filename