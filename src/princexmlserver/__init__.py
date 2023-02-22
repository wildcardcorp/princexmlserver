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

from pyramid.config import Configurator

from princexmlserver.db import Database
from princexmlserver.securitypolicy import PrinceXMLServerSecurityPolicy


logger = logging.getLogger('princexmlserver')


def main(global_config, **settings):
    logger.info('configuring princexmlserver...')

    logger.debug(global_config)
    logger.debug(settings)

    logger.info(f"use_redis: {global_config.get('use_redis', 'not configured')}")
    logger.info(f"redis_url: {settings.get('redis_url', 'not configured')}")
    logger.info(f"dbfilepath: {settings.get('dbfilepath', 'not configured')}")

    use_redis = global_config.get('use_redis', 'false').strip().lower() == 'true'
    redis_url = settings.get('redis_url', 'redis://localhost:6379?health_check_interval=2')
    dbfilepath = settings.get('dbfilepath', 'princexmlserver.db')
    settings["db"] = Database(
        filepath=dbfilepath,
        use_redis=use_redis,
        redis_url=redis_url)

    config = Configurator(settings=settings)
    config.set_security_policy(PrinceXMLServerSecurityPolicy())
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('convert', '/convert')
    config.add_route('ready', '/ready')
    config.include('pyramid_chameleon')
    config.scan()
    return config.make_wsgi_app()
