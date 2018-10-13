from app import app, m, api
from flask import jsonify, request, render_template
from flask_restful import Resource

class Task(Resource):
    def get(self, owner, proyect):
        return jsonify(m.find_task(owner=owner, proyect=proyect))

    def post(self, owner, proyect):
        data = request.form
        m.new_task(
            owner=owner,
            proyect=proyect,
            _id=data['_id'],
            work=data['work'],
            status=data['status']
        )
        return jsonify({'message': 'Yeah!'})
    def put(self, owner, proyect):
        pass

@app.route('/api')
def api_init():
    return render_template('apimoduser.html')

api.add_resource(Task, '/api/<owner>/<proyect>/task')
