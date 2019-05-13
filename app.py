#!/usr/bin/env python3
# app.py

import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_restful import Api
from models.modeldb import mongod
from flask_mail import Mail, Message

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(block_start_string='$$',block_end_string='$$',variable_start_string='$',variable_end_string='$',comment_start_string='$#',comment_end_string='#$'))

app = CustomFlask(__name__)
mail = Mail(app)
app.config.from_pyfile('config.py')

app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'teampmanager@gmail.com',
	MAIL_PASSWORD = 'pmanager123'
	)
mail = Mail(app)
CORS(app)

api = Api(app)
mongo = PyMongo(app)
socketio = SocketIO(app)

m = mongod(mongo)

@app.route('/email')
def email():
    msg = Message("Restablecer tu contraseña",sender=("Pmanager recovery","teampmanager@gmail.com"), recipients=['alexis.luna@alumnos.udg.mx'])
    msg.body = "Accede a la siguente dirección para restablecer tu contraseña. Link."
    mail.send(msg)
    return "Mensaje enviado."

from views import *
from api import *

"""
    Envio de información por el metodo socketio.on a traves de la dirección url/view,
    utilizando el cliente de socketio de javascript para recibir la informacion
    proporcionada astraves del canal view. Este metodo es utilizado por las diferentes
    funciones en el sistema cuando es necesario enviar información para que los usuarios
    la reciban en tiempo real sin recargar su sistema activo.
"""

@socketio.on('message', namespace='/view')
def datas(*msg):
    print(msg)

#port = int(os.getenv('PORT', 5000))
port = os.environ.get("PORT") or os.environ.get("VCAP_APP_PORT") or 5009
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(port))

# if __name__ == '__main__':
#     #app.run(host='0.0.0.0', port=port)
#     socketio.run(app, host='0.0.0.0',port=port)
