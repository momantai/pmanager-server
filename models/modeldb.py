from flask_pymongo import PyMongo
from bson.objectid import ObjectId


class mongod:
    def __init__(self, based):
        self.mong = based
        self.status = ['backlog', 'progress', 'review', 'stop']

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

    def change_status(self, **data):
        if data['typeAction'] == 'change':
            statusI = data['statusI']

            if data['trayectI'] == 'n':
                statusI = self.status[self.status.index(statusI)+1]
            else:
                statusI = self.status[self.status.index(statusI)-1]

            self.mong.db.proyects.update({
                'owner': 'momantai',
                'proyect_id': data['proyect'],
                'task._id': data['idI']
            }, {
                '$set': {
                    'task.$.status': statusI
                }
            }, upsert=False)
        else:
            pass

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
        
