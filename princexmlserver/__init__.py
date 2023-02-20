from pyramid.config import Configurator
from pyramid.request import Request as BaseRequest
from pyramid.decorator import reify

from princexmlserver.db import Database
from princexmlserver.securitypolicy import PrinceXMLServerSecurityPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    use_redis = settings.get('use_redis', False)
    redis_url = settings.get('redis_url', 'redis://localhost:6379?health_check_interval=2')  # noqa
    dbfilepath = settings.get('dbfilepath', 'princexmlserver.db')
    keep_stats = settings.get('keep_stats', 'true').lower() == 'true'

    class Request(BaseRequest):
        @reify
        def db(self):
            return Database(
                filepath=dbfilepath,
                use_redis=use_redis,
                redis_url=redis_url)

        @reify
        def keep_stats(self):
            return keep_stats

    config = Configurator(
        settings=settings,
        request_factory=Request)
    config.set_security_policy(PrinceXMLServerSecurityPolicy())
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('convert', '/convert')
    config.add_route('ready', '/ready')
    config.include('pyramid_chameleon')
    config.scan()
    return config.make_wsgi_app()
