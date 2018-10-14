from app import app, m, api, socketio
from flask import jsonify, request, render_template
from flask_restful import Resource


class Task(Resource):
    def get(self, owner, proyect):
        return jsonify(m.find_task(owner=owner, proyect=proyect))

    def post(self, owner, proyect):
        data = request.form
        print(data)
        m.new_task(
            owner=owner,
            proyect=proyect,
            _id=data['_id'],
            work=data['work'],
            status=data['status']
        )

        socketio.emit('message', data, namespace = '/view')

        return jsonify({'message': 'Yeah!'})
    
    def put(self, owner, proyect):
        data = request.form
        if data['typeAction'] == 'changeStatus':
            s = m.change_task_status(
                owner=owner,
                proyect=proyect,
                _id=data['_id'],
                status=data['status'],
                move=data['move']
            )
            
            data = dict(data)
            data['status'] = s
            socketio.emit('message', data, namespace = '/view')

            return jsonify({'message': 'Yeah!'})

    def delete(self, owner, proyect):
        data = request.args.get('id')
        
        m.delete_task(
            owner=owner,
            proyect=proyect,
            task_id=data
        )

        print(data)

        return jsonify({'message': 'Yeah!', '_id': data})


api.add_resource(Task, '/api/<owner>/<proyect>/task')
