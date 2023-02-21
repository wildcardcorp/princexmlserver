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
