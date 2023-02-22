# Copyright 2023 Wildcard Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import MutableMapping
import dbm
import json
import logging

try:
    import redis
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False

logger = logging.getLogger('princexmlserver')


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
            logger.error('configured to use redis, but no redis available')
            raise ConnectionError("Cannot connect to redis, the 'redis' module is not available")
        elif self.use_redis:
            logger.debug('using redis')
            return RedisDict(self.redis_url)
        else:
            logger.debug('using dbm')
            if self.filepath is None:
                raise ConnectionError(
                    "Cannot connect to dbm file, no filepath specified")
            try:
                return dbm.open(self.filepath, mode)
            except Exception:
                logger.info(f'trying to recreate {self.filepath}')
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
