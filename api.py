from app import app, m, api, socketio
from flask import jsonify, request, render_template
from flask_restful import Resource
from uuid import uuid4
from flask_uploads import UploadSet, configure_uploads, uploaded_file, ALL


file = UploadSet('files', ALL)
configure_uploads(app, file)

class Task(Resource):
    def get(self, owner, proyect):
        return jsonify(m.find_task(owner=owner, proyect=proyect))

    def post(self, owner, proyect):
        data = request.form
        print(data)

        id = str(uuid4())

        tgs = data['tags'].split(',')
        if tgs == ['']:
            tgs = ''
        print(tgs)
        m.new_task(
            owner=owner,
            proyect=proyect,
            _id=id,
            work=data['work'],
            status=data['status'],
            tag = tgs
        )

        data = {'_id': id, 'work': data['work'], 'status': data['status'],'tag': tgs,
                'typeAction': data['typeAction'], 'm': data['m']}

        socketio.emit('message', data, namespace='/view')

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

            socketio.emit('message', data, namespace='/view')

            return jsonify({'message': 'Yeah!'})
        elif data['typeAction'] == 'taskEdit':
            m.edit_task(
                owner=owner,
                proyect=proyect,
                _id=data['_id'],
                work=data['work']
            )
            socketio.emit('message', data, namespace='/view')
        elif data['action'] == 'delete':
            self.delete(owner, proyect, data['_id'])

    def delete(self, owner, proyect, idMovil=""):
        data = request.args.get('id') if idMovil == "" else idMovil

        print(data)
        m.delete_task(owner=owner, proyect=proyect, task_id=data)

        data = request.args if idMovil == "" else {'typeAction': 'deleteTask',
                                                   'm': 'rm',
                                                   'id': idMovil}
        print(data)

        socketio.emit('message', data, namespace='/view')

        return jsonify({'message': 'Yeah!', '_id': data})


class infoTask(Resource):
    def get(self, owner, proyect, id):
        x = m.find_task_info(owner=owner, proyect=proyect, _id=id)

        return jsonify(x)

    def put(self, owner, proyect, id):
        data = request.form

        if data['action'] == 'title':
            m.update_task_title(
                owner=owner,
                proyect=proyect,
                _id=id,
                newTitle=data['newTitle']
            )

            data = {'_id': id, 'work': data['newTitle'], 'typeAction': 'title' }

            socketio.emit('message', data, namespace='/view')

        elif data['action'] == 'description':
            print(data['newDescription'])
            print('*********************')
            m.update_task_description(
                owner=owner,
                proyect=proyect,
                _id=id,
                newDescription=data['newDescription']
            )
        elif data['action'] == 'todo':
            if data['actodo'] == 'create':
                _id = str(uuid4())
                m.create_todo(
                    owner=owner,
                    proyect=proyect,
                    _id = id,
                    _idt= _id,
                    todo = data['todo'],
                    check = ''
                )
                print('Paso la prueba')
                return jsonify({'_id': _id, 'todo': data['todo'], 'check': ''})
            if data['actodo'] == 'update':
                print(data['check'])
                m.update_todo(
                    owner=owner,
                    proyect=proyect,
                    _id=id,
                    idt=data['_id'],
                    todo=data['todo'],
                    check=data['check']
                )
                return jsonify({'ok':'Yeah!'})
            if data['actodo'] == 'delete':
                m.delete_todo(
                    owner=owner,
                    proyect=proyect,
                    _id=id,
                    idt=data['_id']
                )

@app.route('/<owner>/<proyect>/upFile/<_id>', methods=['POST'])
def uploadFile(owner, proyect, _id):
    print('asdasd')
    if request.method == 'POST':
        print('Es post')
    try:
        id = str(uuid4())
        f = file.save(request.files['file'],name=id)
        print(f)

        m.files_to_task(
            owner = owner,
            proyect = proyect,
            _id = _id,
            _idf = id,
            name = request.form['namefile']
        )

        return jsonify({'name': request.form['namefile'], '_id': id})
    except:
        print('No dio')
        return jsonify({'r' : 'Error!'})
@app.route('/subir')
def subir():
    return '''
    <form action="/upFile" enctype="multipart/form-data" method="POST">
    <input type="file" name="file" id="file" required>
    <input type="submit">
    </form>
    '''


api.add_resource(infoTask, '/api/<owner>/<proyect>/t/<id>')
api.add_resource(Task, '/api/<owner>/<proyect>/task')
