from app import app
from app import socketio, m
import json
from bson.json_util import dumps
from flask_socketio import send
import uuid
from flask import jsonify

@app.route('/')
def index():
    return '<h1>Page Index to Plam - Manager</h1>'


@app.route('/json')
def son():
    return jsonify(m.find_task(owner='momantai', proyect='5bbd24f8bc5fd60d3d436b22'))

@app.route('/newTask/<work>/<status>')
def newTask(work, status):
    _id = str(uuid.uuid4())
    m.newTask(
        work=work,
        status=status,
        _id=_id
    )
    
    return jsonify({'_id': _id,'data':work, 'status': status})


@socketio.on('message', namespace='/view')
def headMessage(*msg):
    m.change_status(typeAction=msg[0]['typeAction'],
             idI=msg[0]['idI'],
             statusI=msg[0]['statusI'],
             trayectI=msg[0]['trayectI'])

    send(msg, broadcast=True)
