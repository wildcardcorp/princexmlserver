import anydbm
import json


class Database(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def _open(self, mode='r'):
        try:
            return anydbm.open(self.filepath, mode)
        except:
            # might not be created yet, create, close
            # open again with whatever mode
            db = anydbm.open(self.filepath, 'n')
            db.close()
            return self._open(mode)

    def get(self, name, default=None):
        db = self._open()
        try:
            return json.loads(db[name])
        except KeyError:
            return default

    def put(self, name, value):
        db = self._open('c')
        db[name] = json.dumps(value)
