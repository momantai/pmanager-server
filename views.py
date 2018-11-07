from flask import render_template
from app import app

@app.route('/')
def index():
    return '<h1>Page Index to PManager</h1>'

@app.route('/api')
def api_init():
    return render_template('apimoduser.html')