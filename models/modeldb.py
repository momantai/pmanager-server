from flask_pymongo import PyMongo
from bson.objectid import ObjectId


class mongod:
    def __init__(self, based):
        self.mong = based
        self._status = ['backlog', 'progress', 'review', 'stop']

    def find_task(self, **data):
        return self.mong.db.proyects.find_one({
            'owner': data['owner'],
            'proyect_id': data['proyect']
        }, {
            '_id': 0,
            'task': 1,
            'task.work': 1,
            'task.status': 1,
            'task._id': 1
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
                    'status': data['status']
                }
            }
        })

    def change_task_status(self, **data):
        status = data['status']
        if data['move'] == 'n':
            status = self._status[self._status.index(status)+1]
        else:
            status = self._status[self._status.index(status)-1]

        self.mong.db.proyects.update(
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
