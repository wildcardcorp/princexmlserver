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

import unittest

from pyramid import testing

from princexmlserver.db import Database
from princexmlserver.views import home
from princexmlserver.views import ready


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_settings({
            "db": Database(
                filepath="/tmp/princexmlserver.db",
                use_redis=False,
                redis_url=None),
        })

    def tearDown(self):
        testing.tearDown()

    def test_ready(self):
        req = testing.DummyRequest()
        resp = ready(req)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, "ready")

    def test_home(self):
        req = testing.DummyRequest()
        resp = home(req)
        self.assertEqual(len(resp["stat_rows"]), 1)
        self.assertEqual(resp["stat_rows"][0]["tag_name"], "all")
        self.assertEqual(resp["stat_rows"][0]["conversion_count"], 0)
