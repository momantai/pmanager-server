from flask_pymongo import PyMongo
from bson.objectid import ObjectId


class mongod:
    def __init__(self, based):
        self.mong = based
        self._status = ['Backlog', 'Progress', 'Review', 'Stop']

    def find_task(self, **data):
        return self.mong.db.proyects.find_one({
            'owner': data['owner'],
            'proyect_id': data['proyect']
        }, {
            '_id': 0,
            'task': 1,
            'task.work': 1,
            'task.status': 1,
            'task._id': 1,
            'task.tag': 1
        })

    def new_task(self, **data):
        self.mong.db.proyects.update_one({
            'owner': data['owner'],
            'proyect_id': data['proyect']
        }, {
            '$push': {
                'task': {
                    '_id': data['_id'],
                    'work': data['work'],
                    'status': data['status'],
                    #'description': '',
                    'tag': data['tag'],
                    'resources': [],
                    'todo': []
                }
            }
        })

    def files_to_task(self, **data):
        self.mong.db.proyects.update_one({
            'owner': data['owner'],
            'proyect_id': data['proyect'],
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
                'owner': 'momantai',
                'proyect_id': data['proyect'],
                'task._id': data['_id']
            }, {
                '$set': {
                    'task.$.status': status
                }
            }, upsert=False)
        return status

    def edit_task(self, **data):
        self.mong.db.proyects.update(
            {
                'owner': 'momantai',
                'proyect_id': data['proyect'],
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
                'owner': data['owner'],
                'proyect_id': data['proyect']
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
    def find_task_info(self, **data):
        return self.mong.db.proyects.find_one({
            'task._id': data['_id']
        }, {
            'task.$[0]': 1,
            '_id': 0
        })
    def update_task_title(self, **data):
        self.mong.db.proyects.update(
            {
                'owner': data['owner'],
                'proyect_id': data['proyect'],
                'task._id': data['_id']
            }, {
                '$set': {
                    'task.$.work': data['newTitle']
                }
            }, upsert=False)
    def update_task_description(self, **data):
        self.mong.db.proyects.update(
            {
                'owner': data['owner'],
                'proyect_id': data['proyect'],
                'task._id': data['_id']
            }, {
                '$set': {
                    'task.$.description': data['newDescription']
                }
            }, upsert=False)
    # Todo list
    def create_todo(self, **data):
        self.mong.db.proyects.update_one({
            'owner': data['owner'],
            'proyect_id': data['proyect'],
            'task._id': data['_id']
        }, {
            '$push': {
                'task.$.todo': {
                    '_id': data['_idt'],
                    'todo': data['todo'],
                    'check': data['check']
                }
            }
        })

    def update_todo(self, **data):
        print('Entro')
        self.mong.db.proyects.update_one(
            {
                'owner': data['owner'],
                'proyect_id': data['proyect'],
            }, 
                {
                    '$set': {
                        'task.$[i].todo.$[j].todo': data['todo'],
                        'task.$[i].todo.$[j].check': data['check']
                    }
                }, array_filters= [{"i._id": data['_id']}, {"j._id": data['idt']}])

        print('Salio')
    def delete_todo(self, **data):
        self.mong.db.proyects.update(
            {
                'owner': data['owner'],
                'proyect_id': data['proyect'],
                'task._id': data['_id']
            },{
                '$pull': {
                    'task.$.todo': {
                        '_id': data['idt']
                        
                    }
                }
            }
        )

    def findprojects(self, **data):
        print("Hola")
        return self.mong.db.proyects.find({
            'collaborators': 'momantai'
        }, {
            '_id':0,
            'title': 1,
            'owner': 1,
            'letters': 1,
            'proyect_id': 1,
            'task.status': 1
        })

    def find_project(self, **data):
        return self.mong.db.proyects.find_one(
            {
                'owner': data['owner'],
                'proyect_id': data['proyect']
            },
            {
                '_id': 0,
                'title': 1,
                'description': 1,
                'collaborators': 1,
                'owner': 1,
                'proyect_id': 1
            }
        )
    def update_project(self, **data):
        self.mong.db.proyects.update_one(
            {
                'owner': data['owner'],
                'proyect_id': data['proyect']
            },
            {
                '$set': {
                    'title': data['title'],
                    'description': data['description']
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
                    'proyect_id': data['_id'],
                    'owner': data['owner'],
                    'collaborators': u['user']
                }, {
                    'proyect_id': 1,
                    '_id': 0
                }
            )
            if p == None:
                self.mong.db.proyects.update_one(
                    {
                        'proyect_id': data['_id'],
                        'owner': data['owner']
                    },{
                        '$push': {
                            'collaborators': u['user']
                        }
                    }
                )
                return {'ok':'ok'}
            else:
                return {'ok':'UenP'}
        else:
            return {'ok':'UnoE'}
    
    def create_project(self, **data):
        p = self.mong.db.proyects.find_one(
            {
                'proyect_id': data['_id'],
                'owner': data['owner']
            }, {
                'proyect_id': 1,
                '_id': 0
            }
        )

        if p == None:
            print('¡Insertando datos!')
            self.mong.db.proyects.insert_one(
                {
                    'title': data['title'],
                    'proyect_id': data['_id'],
                    'owner': data['owner'],
                    'description': '',
                    'collaborators': [data['owner']],
                    'task': []
                }
            )
            return {'ok':'ok'}
        print('¡Dato existente!')
        return {'ok': 'exist'}