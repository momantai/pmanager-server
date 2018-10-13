from flask_pymongo import PyMongo
from bson.objectid import ObjectId


class mongod:
    def __init__(self, based):
        self.mong = based
        self.status = ['backlog', 'progress', 'review', 'stop']

    def find_task(self, **data):
        return self.mong.db.proyects.find_one({'owner': data['owner'], '_id': ObjectId(data['id'])}, {'_id': 0, 'task': 1, 'task.work': 1, 'task.status': 1, 'task._id': 1})

    def change(self, **data):
        if data['typeAction'] == 'change':
            idI = data['idI']
            statusI = data['statusI']
            trayectI = data['trayectI']
            print(statusI)
            if trayectI == 'n':
                statusI = self.status[self.status.index(statusI)+1]
            else:
                statusI = self.status[self.status.index(statusI)-1]

            self.mong.db.proyects.update({
                'owner': 'momantai', 'task._id': idI
            },
                {
                    '$set': {
                        'task.$.status': statusI
                    }
            }, upsert=False)
        else:
            pass
