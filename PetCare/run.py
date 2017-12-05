import os
from flask import Flask
from blueprints.PetCare import init_db, close_db, bp

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE = os.path.join(app.root_path, 'PetCare.db'),
	SECRET_KEY = 'SECRET_KEY',
	USERNAME = 'admin',
	PASSWORD = 'password',
	UPLOADED_IMAGES_DEST = "PetCare/static/images/"
))
app.config.from_envvar('PETCARE_SETTINGS', silent=True)

@app.cli.command('initdb')
def initdb_command():
	init_db()

@app.teardown_appcontext
def closedb(error):
	close_db()

app.register_blueprint(bp)