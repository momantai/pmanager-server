from app import app, m, api, socketio
from flask import jsonify, request, render_template
from flask_restful import Resource
from uuid import uuid4
from flask_uploads import UploadSet, configure_uploads, uploaded_file, ALL
import random

# Configuracion para subir archivos.

file = UploadSet('files', ALL)
configure_uploads(app, file)


class projects(Resource):
    """
        Consulta proyetos propietarios y proyectos en los que un usuario colabora, asi como tambien utiliza la funcion de crear nuevos proyectos y eliminarlos. Interactua a traves del protocolo HTTP con los siguientes metodos:
        url + '/api/projects/<cola>'
        En donde:
            <cola> : Es el nombre de usuario.
        Metodos:
            GET: Consulta los proyectos en los que estas trabajando, los valores recibidos en la consulta son:
                {
                    title,
                    owner,
                    letters,
                    proyect_id
                }
            PUT: Crear un nuevo proyecto.
                {
                    title,
                    _id
                }
    """
    def get(self, cola):
        res = []
        
        # [res.append(i) for i in m.find_projects(team=cola)]
        res = m.find_projects(team=cola)
        return res
    
    def put(self, cola):
        data = request.form
        print(cola)
        #print(data['title'])
        r = m.create_project(
            leader = cola,
            title = data['title'],
            _id = str(uuid4()) # data['_id']
        )

        print('Resando')

        return jsonify(r)

class project(Resource):
    """
        Consulta los detalles y colaboradores de un proyecto en el que trabajas. Para interactuar hazlo a traves del protocolo HTTP, utilizando los metodos que se te muestran mas adelante.
        '/api/project/<owner>/<proyect>'
        En donde:
            <owner> : usuario propietario del proyecto consultado.
            <proyecto> : identificador del proyecto a consultar.
        Metodos a utilizar:
            GET: Consulta los detalles del proyecto. Y recibe la siguiente informacion:
                {
                    title,
                    description,
                    collaborators,
                    owner,
                    proyect_id
                }
            PUT: Metodo para actualizar informacion de los detalles de un proyecto y agregar nuevos colaboradores a un proyecto (utilizando el mismo metodo gracias a un parametro que lo permite).
                // Actualizar datalles de proyecto.
                {
                    type,
                    title,
                    description
                }
                // Agregar colaborador nuevo.
                {
                    type,
                    collaborator
                }
    """
    def get(self, owner, proyect):
        p = m.find_project(
            leader=owner,
            proyect=proyect
        )
        return jsonify(p)
    def put(self, owner, proyect):
        data = request.form
        print(data['type'])
        
        if data['type'] == 'updateTitle':
            m.update_project_title(
                leader=owner,
                proyect=proyect,
                title = data['title']
            )
            return jsonify({'ok':'ok'})
        elif data['type'] == 'updateDetails':
            m.update_project_details(
                leader=owner,
                proyect=proyect,
                details = data['description']
            )
            return jsonify({'ok':'ok'})
        elif data['type'] == 'addcoll':
            print("Momantai")

            c = m.add_collaborator(
                _id = proyect,
                leader = owner,
                team = data['collaborator']
            )

            return jsonify(c)
        elif data['type'] == 'deleteProject':
            print(data['sure'])
            if data['sure'] == 'true':
                m.delete_project(
                    _id = proyect,
                    leader = owner
                )
                return jsonify({'status': True})
            return jsonify({'status': False})
        return jsonify({'status': 'error'})

class thingsTodo(Resource):
    """
        Interactua con información muy superficial de las tareas encontradas en un proyecto, al permitir hacer una seleccion por tarea, moverlas de lugar, eliminarlas y abrir los detalles de dichas tareas, pero sin proveer la información de dichos detalles pues de eso se encarga una clase que veremos más adelante, para despues ser modificados.
        La forma correcta de interactuar con esta clase a traves del protocolo HTTP es la siguiente:
            url + '/api/<owner>/<proyect>/task'
            En donde:
                <owner> : Es el usuario propietario del proyecto al que se accede.
                <proyect> : Es el identificador del proyecto al que intentas acceder.
            
            Utilizando los metodos del protocolo HTTP:
                GET: Recibe informacion a traves de este metodo sin más parametros que la direccion proporcionada al hacer la consulta, los valores recibidos son:
                    //Lista de tareas
                    task [
                        // Tarea
                        {
                            _id,
                            work,
                            status,
                            tag
                        }
                    ]
                POST: Después de enviar los valores a traves de este metodo recibiras una respuesta a traves de SocketIO como comprobacion de que tu informacion fue almacenada satisfactoriamente, los valores que deberas enviar son:
                    // Crear tarea
                    {
                        work,
                        status,
                        tags
                    }
                PUT: Este metodo es utilizado para realizar varias instrucciones, asi que segun sea el caso los datos a enviar cambiaran un poco, tal como:
                    // Cambiar tarea de estado
                    {
                        _id,
                        status,
                        move,
                        typeAction
                    }
                    // Editar nombre de tarea
                    {
                        _id,
                        work,
                        typeAction
                    }
                    // Eliminar tarea (si no te funciona el metodo delete).
                    {
                        _id,
                        action
                    }
                DELETE: Eliminar tareas, a traves de un unico valor enviado.
                    {
                        id
                    }
    """
    def get(self, owner, proyect):
        return jsonify(m.find_task(leader=owner, proyect=proyect))

    def post(self, owner, proyect):
        data = request.form
        print(data)

        id = str(uuid4())

        tgs = data['tags'].split(',')
        if tgs == ['']:
            tgs = ''
        print(tgs)
        m.new_task(
            leader=owner,
            proyect=proyect,
            _id=id,
            name=data['name'],
            status=data['status'],
            tag=tgs
        )

        data = {'_id': id, 'name': data['name'], 'status': data['status'], 'tag': tgs,
                'typeAction': data['typeAction'], 'isproject': proyect}

        socketio.emit('message', data, namespace='/view')

        return jsonify({'message': 'Yeah!'})

    def put(self, owner, proyect):
        data = request.form
        if data['typeAction'] == 'changeStatus':
            s = m.change_task_status(
                leader=owner,
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
                leader=owner,
                proyect=proyect,
                _id=data['_id'],
                work=data['work']
            )
            socketio.emit('message', data, namespace='/view')
        elif data['typeAction'] == 'deleteTask':
            m.delete_task(
                _listid = data['list'],
                _id = data['_id']
            )
            data = {'typeAction': 'deleteTask', 'list': data['list'], '_id': data['_id']}
            socketio.emit('message', data, namespace='/view')
            return jsonify(data)

    def delete(self, owner, proyect, idMovil=""):
        data = request.args.get('id') if idMovil == "" else idMovil

        print(data)
        m.delete_task(leader=owner, proyect=proyect, task_id=data)

        data = request.args if idMovil == "" else {'typeAction': 'deleteTask',
                                                   'm': 'rm',
                                                   'id': idMovil}
        print(data)

        socketio.emit('message', data, namespace='/view')

        return jsonify({'message': 'Yeah!', '_id': data})

class Task(Resource):
    """
        Gestiona los detalles y la informacion que acompania a una tarea dentro de un taskboard.
        url + '/api/<owner>/<proyect>/t/<id>'
        En donde:
            <owner> : usuario propietario del proyecto en el que se esta.
            <proyect> : identificador del proyecto.
            <id>: identeficador de la tarea a la que se intenta acceder.
        Metodos utilizados:
            GET: Consultar detalles de una tarea dentro de un proyecto, los siguientes valores son la respuesta de la consulta:
                {
                    _id,
                    work,
                    status,
                    description,
                    resources[],
                    todo[]
                }
            PUT: Metodo con el cual podras realizar diferentes cosultas gracias a un parametro (action) que nos lo permite. En este caso envias los siguientes valores:
                // Actualizar titulo de tarea
                {
                    newTitle,
                    action
                }
                // Actualizar descripcion
                {
                    newDescription,
                    action
                }
                # Entramos a la parte de ToDo dentro de una tarea
                    // Nuevo todo
                    {
                        action,
                        actiontodo,
                        todo
                    }
                    //Editar todo
                    {
                        action,
                        actiontodo,
                        _id,
                        todo,
                        check
                    }
                    //Eliminar todo
                    {
                        action,
                        actiontodo,
                        _id
                    }
    """
    def get(self, owner, proyect, id):
        x = m.find_task_info(leader=owner, proyect=proyect, _id=id)

        return jsonify(x)

    def put(self, owner, proyect, id):
        data = request.form

        if data['action'] == 'title':
            m.update_task_title(
                leader=owner,
                proyect=proyect,
                _id=id,
                newTitle=data['newTitle']
            )

            data = {'_id': id, 'name': data['newTitle'], 'sta': data['sta'],'typeAction': 'title', 'isproject': proyect }
            print(data)
            socketio.emit('message', data, namespace='/view')

        elif data['action'] == 'description':
            #print(data['newDescription'])
            print('*********************')
            m.update_task_details(
                _id=id,
                newdetails=data['newdetails']
            )
        elif data['action'] == 'todo':
            if data['actodo'] == 'create':
                _id = str(uuid4())
                m.create_todo(
                    leader=owner,
                    proyect=proyect,
                    _id = id,
                    _idt= _id,
                    todo = data['todo'],
                    check = ''
                )
                print('Paso la prueba')
                return jsonify({'_id': _id, 'todo': data['todo'], 'check': ''})
            if data['actodo'] == 'update':
                m.update_todo(
                    leader=owner,
                    proyect=proyect,
                    _id=id,
                    idt=data['_id'],
                    todo=data['todo'],
                    check=data['check']
                )
                return jsonify({'ok':'ok'})
            if data['actodo'] == 'delete':
                m.delete_todo(
                    leader=owner,
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
            leader = owner,
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

class test(Resource):
    # s = m.change_task_status(
    #             owner=owner,
    #             proyect=proyect,
    #             _id=data['_id'],
    #             status=data['status'],
    #             move=data['move']
    #         )
    def get(self, action):
        if action == 'mstatus':
            m.find_test()
            return jsonify({'Hola': 1})

class listsProject(Resource):
    def post(self, leader, project):
        data = request.form
        print(data)
        if 'movetolist' == data['action']:
            print('adkasdqwdiqw diqwdioqwdo')
            print(data)
            m.movetolist(
                _id = data['element'],
                final = data['final'],
                futureIndex = data['futureIndex']
            )  

            rdata = {'element': data['element'], 'init': data['init'], 'final': data['final'], 'index': data['index'], 'futureIndex': data['futureIndex'], 'typeAction': data['action'], 'isproject': project}

            socketio.emit('message', rdata, namespace='/view')
        elif 'newlist' == data['action']:
            rdata = m.newlist(
                _id = project,
                leader = leader,
                name = data['name']
            )
            rdata.update({'isproject': project})
            socketio.emit('message', rdata, namespace='/view')
        elif 'updatenamelist' == data['action']:
            m.changenamelist(
                _id = project,
                leader = leader,
                _idlist = data['_id'],
                namelist = data['namelist']
            )
            return jsonify({'status': True})

class usersignup(Resource):
    def post(self):
        data = request.form
        return m.signup(
            user = data['user'],
            email = data['email'],
            first_name = data['first_name'],
            last_name = data['last_name'],
            password = data['password']
        )

class usersignin(Resource):
    def post(self):
        data = request.form
        print(data)
        return m.signin(
            user = data['user'],
            password = data['password']
        )

class comments(Resource):
    def get(self, leader, project, id):
        #data = request.form

        commentsdata = m.getcomments(
            _idtask = id
        )
        print(commentsdata)
        return [i for i in commentsdata]
    def post(self, leader, project, id):
        data = request.form
        print(data)
        d = m.comment(
            user = data['user'],
            commentary = data['commentary'],
            _idtask = id
        )

        return jsonify({'usercomment': data['user'], 'commentary': data['commentary'], '_idcomment': d['_idcomment']})

@app.route('/api/identify')
def identeficar():
    key = request.args.get('key')
    return identify(m, key)

# Indentify
def identify(db, key):
    return db.identify(key = key)

@app.route('/api/search-user/<username>')
def search_user(username):
    return jsonify(m.search_user(
        username = username
    ))

api.add_resource(Task, '/api/<owner>/<proyect>/t/<id>')
api.add_resource(thingsTodo, '/api/<owner>/<proyect>/task')
api.add_resource(projects, '/api/projects/<cola>')
api.add_resource(project, '/api/project/<owner>/<proyect>')
api.add_resource(test, '/test/<action>')
api.add_resource(listsProject, '/api/<leader>/<project>/l')
api.add_resource(usersignup, '/api/user/signup')
api.add_resource(usersignin, '/api/user/signin')
api.add_resource(comments, '/api/<leader>/<project>/t/<id>/c')
