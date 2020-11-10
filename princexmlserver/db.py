import dbm
import json


class Database(object):
    def __init__(self, filepath):
        self.filepath = filepath

    def _open(self, mode='r'):
        try:
            return dbm.open(self.filepath, mode)
        except Exception:
            # might not be created yet, create, close
            # open again with whatever mode
            db = dbm.open(self.filepath, 'n')
            db.close()
            return self._open(mode)

    def get(self, name, default=None):
        db = self._open()
        try:
            return json.loads(db[name].decode('utf-8'))
        except KeyError:
            return default

    def put(self, name, value):
        db = self._open('c')
        db[name] = json.dumps(value)
