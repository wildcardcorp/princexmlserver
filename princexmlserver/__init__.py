from pyramid.config import Configurator
from pyramid.request import Request as BaseRequest
from princexmlserver.db import Database
from pyramid.decorator import reify


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    dbfilepath = settings.get('dbfilepath', 'princexmlserver.db')
    keep_stats = settings.get('keep_stats', 'true').lower() == 'true'

    class Request(BaseRequest):
        @reify
        def db(self):
            return Database(dbfilepath)

        @reify
        def keep_stats(self):
            return keep_stats

    config = Configurator(
        settings=settings,
        request_factory=Request)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('convert', '/convert')
    config.include('pyramid_chameleon')
    config.scan()
    return config.make_wsgi_app()
