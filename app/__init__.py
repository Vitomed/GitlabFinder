import logging
import os

from config import ConfigApp
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from gitlab import Gitlab
from logging.handlers import RotatingFileHandler


def create_app(config: object):
    app = Flask(__name__)
    app.config.from_object(config)
    return app


app = create_app(ConfigApp)
db = SQLAlchemy(app)
# migrate = Migrate(app, db)
gl = Gitlab('https://gitlab.com/', private_token='mpFQR4rh6EsP4UyP1wMK')

from app import routes, models

db.create_all()
if not app.debug:

    if not os.path.exists('log'):
        os.mkdir('log')

    file_handler = RotatingFileHandler('log/gitlab.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Gitlab API project startup')
