from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_restful import Api
from models.modeldb import mongod


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(block_start_string='$$',block_end_string='$$',variable_start_string='$',variable_end_string='$',comment_start_string='$#',comment_end_string='#$'))

app = CustomFlask(__name__)
app.config.from_pyfile('config.py')
CORS(app)

api = Api(app)
mongo = PyMongo(app)
socketio = SocketIO(app)

m = mongod(mongo)

from views import *
from api import *

if __name__ == '__main__':
    socketio.run(app)