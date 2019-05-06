from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from uuid import uuid4

class mongod:
    def __init__(self, based):
        self.mong = based
        self._status = ['Backlog', 'Progress', 'Review', 'Stop']

    def find_task(self, **data): # Bien
        b = self.mong.db.proyects.find_one({
            'leader': data['leader'],
            'project_id': data['proyect']
        }, {
            '_id': 0,
            'board': 1
        })['board']
        c = []
        for i in b:
            t = self.mong.db.thingstodo.find_one(
                {
                    '_thingstoid': i['_id']
                },{
                    '_id': 0,
                    #'things': 1
                }
            )
            c.append(t)
        
        dxta = {'lists': b,'liststodo': c}

        return dxta
    
    def find_test(self):
        dx = self.mong.db.proyects.find_one(
            {
                'project_id': 'nuevo'
            },{
                '_id':0,
                'board': 1
            }
        )
        listsearch = [i['_id'] for i in dx['board']]
        dt = self.mong.db.task_todo.find(
            {'_idl': {'$in': listsearch}},{'_id':0}
        )

        for i in dt:
            print(i)

    def move_task(self, **data):
        self.mong.db.proyects.update_one({
            'leader': data['leader'],
            'project_id': data['proyect']
        })

    def new_task(self, **data): # Faltan cosas
        self.mong.db.thingstodo.update_one({
            '_thingstoid': data['status']
        }, {
            '$push': {
                'things': {
                    '_id': data['_id'],
                    'name': data['name'],
                    #'status': data['status'],
                    'details': '',
                    # 'tag': data['tag'],
                    # 'resources': [],
                    # 'todo': []
                }
            }
        })

        self.mong.db.resources.insert_one({
            '_resourceid': data['_id'],
            'todo': [],
            'resources': []
        })

    def files_to_task(self, **data):
        self.mong.db.proyects.update_one({
            'leader': data['leader'],
            'project_id': data['proyect'],
            'task._id': data['_id']
        }, {
            '$push': {
                'task.$.resources': {
                    '_id': data['_idf'],
                    'name': data['name']
                }
            }
        })

    def change_task_status(self, **data):
        status = data['status']
        if data['move'] == 'n':
            status = self._status[self._status.index(status)+1]
        else:
            status = self._status[self._status.index(status)-1]

        self.mong.db.proyects.update_one(
            {
                'leader': 'momantai',
                'project_id': data['proyect'],
                'task._id': data['_id']
            }, {
                '$set': {
                    'task.$.status': status
                }
            }, upsert=False)
        return status
    
    def change_task_tolist(self, **data):
        return str(data['leader'])

    def edit_task(self, **data):
        self.mong.db.proyects.update(
            {
                'leader': 'momantai',
                'project_id': data['proyect'],
                'task._id': data['_id']
            }, {
                '$set' : {
                    'task.work': data['work']
                }
            }
        )

    def delete_task(self, **data):
        self.mong.db.proyects.update(
            {
                'leader': data['leader'],
                'project_id': data['proyect']
            },
            {
                '$pull': {
                    'task': {
                        '_id': data['task_id']
                    }
                }
            }
        )
    
    #CRUD task info
    def find_task_info(self, **data): # Faltan cosas
        info = self.mong.db.thingstodo.find_one({
            'things._id': data['_id'] 
        }, {
            'things.$[0]': 1,
            '_id': 0
        })

        resource = self.mong.db.resources.find_one({
            '_resourceid': data['_id']
        }, {
            '_id': 0,
            '_resourceid': 0
        })

        i = str(info)

        

        return {'things': info['things'][0], 'resource': resource}

    def update_task_title(self, **data): # Bien
        self.mong.db.thingstodo.update(
            {
                'things._id': data['_id']
            }, {
                '$set': {
                    'things.$.name': data['newTitle']
                }
            }, upsert=False)
    def update_task_details(self, **data): # Bien
        self.mong.db.thingstodo.update(
            {
                'things._id': data['_id']
            }, {
                '$set': {
                    'things.$.details': data['newdetails']
                }
            }, upsert=False)
    # Todo list
    def create_todo(self, **data):
        self.mong.db.resources.update_one({
            '_resourceid': data['_id']
        }, {
            '$push': {
                'todo': {
                    '_id': data['_idt'],
                    'todo': data['todo'],
                    'check': data['check']
                }
            }
        })

    def update_todo(self, **data):
        print('Entro')
        self.mong.db.resources.update_one(
            {
                '_resourceid': data['_id'],
                'todo._id': data['idt']
            }, 
                {
                    '$set': {
                        'todo.$.todo': data['todo'],
                        'todo.$.check': data['check']
                    }
                }) # , array_filters= [{"i._id": data['_id']}, {"j._id": data['idt']}])

        print('Salio')
    def delete_todo(self, **data):
        self.mong.db.resources.update(
            {
                # 'leader': data['leader'],
                # 'project_id': data['proyect'],
                '_resourceid': data['_id']
            },{
                '$pull': {
                    'todo': {
                        '_id': data['idt']
                        
                    }
                }
            }
        )

    def find_projects(self, **data): # Faltan cosas
        print("Hola")
        return self.mong.db.proyects.find({
            'team': 'momantai'
        }, {
            '_id':0,
            'title': 1,
            'leader': 1,
            'project_id': 1,
        })

    def find_project(self, **data): # Bien
        return self.mong.db.proyects.find_one(
            {
                'leader': data['leader'],
                'project_id': data['proyect']
            },
            {
                '_id': 0,
                'title': 1,
                'details': 1,
                'team': 1,
                'leader': 1,
                'project_id': 1
            }
        )
    def update_project(self, **data): # Bien
        self.mong.db.proyects.update_one(
            {
                'leader': data['leader'],
                'project_id': data['proyect']
            },
            {
                '$set': {
                    'title': data['title'],
                    'details': data['details']
                }
            }
        )
    def add_collaborator(self, **data):
        u = self.mong.db.users.find_one({
            '$or': [{
                'user': data['collaborator']
            }, {
                'mail': data['collaborator']
            }]
        },
            {
                'user': 1,
                '_id': 0
        })
        
        if u != None:
            p = self.mong.db.proyects.find_one(
                {
                    'project_id': data['_id'],
                    'leader': data['leader'],
                    'team': u['user']
                }, {
                    'project_id': 1,
                    '_id': 0
                }
            )
            if p == None:
                self.mong.db.proyects.update_one(
                    {
                        'project_id': data['_id'],
                        'leader': data['leader']
                    },{
                        '$push': {
                            'team': u['user']
                        }
                    }
                )
                return {'ok':'ok'}
            else:
                return {'ok':'UenP'}
        else:
            return {'ok':'UnoE'}
    
    def newlist(self, **data):
        idlist = str(uuid4())

        self.mong.db.proyects.update_one({
            'project_id': data['_id'],
            'leader': data['leader']
        }, {
            '$push': {
                'board': {'_id': idlist, 'td': data['name']}
            }
        })
        self.mong.db.thingstodo.insert_one(
            {
                '_thingstoid': idlist,
                'things': []
            }
        )

        return {'_id': idlist, 'td': data['name'], 'typeAction': 'newlist'}

    def movetolist(self, **data):
        info = self.mong.db.thingstodo.find_one({
            'things._id': data['_id'] 
        }, {
            'things.$[0]': 1,
            '_id': 0
        })['things'][0]

        self.mong.db.thingstodo.update({
            'things._id': data['_id']
        }, {
            '$pull': {
                'things': {
                    '_id': data['_id']
                }
            }
        })

        self.mong.db.thingstodo.update({
            '_thingstoid': data['final']
        }, {
            '$push': {
                'things': {
                    '$each': [info],
                    '$position': int(data['futureIndex'])
                }
            }
        })

        print('Movido')


    def create_project(self, **data): # Faltan cosas
        p = self.mong.db.proyects.find_one(
            {
                'project_id': data['_id'],
                'leader': data['leader']
            }, {
                'project_id': 1,
                '_id': 0
            }
        )

        print('Paso por aqui')

        if p == None:
            print('Insertando datos')
            idlist = str(uuid4())
            self.mong.db.proyects.insert_one(
                {
                    'title': data['title'],
                    'project_id': data['_id'],
                    'leader': data['leader'],
                    'details': '',
                    'team': [data['leader']],
                    'board': [{'_id': idlist, 'td': '¿Qué hacer?'}]
                }
            )
            idtask = str(uuid4())
            self.mong.db.thingstodo.insert_one(
                {
                    '_thingstoid': idlist,
                    'things': [{'_id': idtask, 'name': '¡Comienza a agregar nuevas listas y tareas a tu proyecto {}!'.format(data['title'])}]
                }
            )

            self.mong.db.resources.insert_one({
                '_resourceid': idtask,
                'todo': [],
                'resources': []
            })

            print('Hubo errorrrrrrrrrr')
            return {'ok':'ok'}
        print('Dato existente')
        return {'ok': 'exist'}