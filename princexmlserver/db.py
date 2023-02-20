from collections.abc import MutableMapping
import dbm
import json

try:
    import redis
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False


# really simple dict interface for redis
# NOTE: only objects being get/set with this are stringified json objects, ints or floats
class RedisDict(MutableMapping):
    def __init__(self, redis_url, *args, **kwargs):
        self.rconn = redis.from_url(redis_url)
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        if self.rconn.exists(key) > 0:
            return self.rconn.get(key)
        else:
            raise KeyError()

    def __setitem__(self, key, value):
        self.rconn.set(key, value)

    def __delitem__(self, key):
        self.rconn.delete(key)

    def __iter__(self):
        return self.rconn.keys()

    def __len__(self):
        return len(self.rconn.keys())


class Database(object):
    def __init__(self, filepath=None, use_redis=False, redis_url=None):
        self.filepath = filepath
        self.use_redis = use_redis
        self.redis_url = redis_url

    def _open(self, mode='r'):
        if self.use_redis and not REDIS_AVAILABLE:
            raise ConnectionError("Cannot connect to redis, the 'redis' module is not available")
        elif self.use_redis:
            return RedisDict(self.redis_url)
        else:
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
            return json.loads(db[name])
        except KeyError:
            return default

    def put(self, name, value):
        db = self._open('c')
        db[name] = json.dumps(value)
