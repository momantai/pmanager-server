from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)

mongo = PyMongo(app)
socketio = SocketIO(app)

from views import *

if __name__ == '__main__':
    socketio.run(app)