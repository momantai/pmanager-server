from app import app
from app import mongo, socketio
import json
from bson.json_util import dumps
from flask_socketio import send

from models.modeldb import mongod

m = mongod(mongo)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("test.html", db=dbb)


@app.route('/json', methods=['GET'])
def son():
    return dumps(m.find_task(owner='momantai', id='5bbd24f8bc5fd60d3d436b22'))

@app.route('/plam')
def lam():
    return '<h1>Plam</h1>'

@socketio.on('message', namespace='/view')
def headMessage(*msg):
    m.change(typeAction=msg[0]['typeAction'],
             idI=msg[0]['idI'],
             statusI=msg[0]['statusI'],
             trayectI=msg[0]['trayectI'])

    send(msg, broadcast=True)