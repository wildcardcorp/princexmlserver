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

import logging
import os

from pyramid.authentication import extract_http_basic_credentials
from pyramid.security import Allowed, Denied


logger = logging.getLogger('princexmlserver')


class PrinceXMLServerSecurityPolicy(object):
    def identity(self, req):
        ident = extract_http_basic_credentials(req)
        if ident is None:
            return None

        ident_key = f"X_API_KEY_{ident.username}".upper()
        psk = os.environ.get(ident_key, None)
        if psk != ident.password:
            return None

        return ident.username

    def authenticated_userid(self, req):
        ident = self.identity(req)
        if ident is None:
            return None
        return ident

    def permits(self, req, ctx, perm):
        api_keys_enabled = os.environ.get('ENABLE_API_KEYS', 'false')
        if api_keys_enabled.strip().lower() == 'false':
            return Allowed('allowed')

        ident = self.identity(req)
        if ident is None:
            return Denied('not allowed')
        else:
            return Allowed('allowed')

    def remember(req, userid, **kw):
        return []  # keep no memory

    def forget(req, **kw):
        return []  # no memory is kept
