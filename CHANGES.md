PrinceXML Server
================

1.0.0 (unreleased)
------------------

- reorg project to separate test code and src
- update setup.py attributes
- add OSS license information
- update Dockerfile to be multi-stage and install princexmlserver through built wheel
- add development.ini and rename production.ini to docker.ini
- move test.py to example.py
- improve test configuration, and add a couple of basic tests as an example
- update requirements.in to be less specific
- update documentation (readme)
- update Makefile targets
- update docker-compose config
- remove custom Request factor on configurator, and move the custom properties to
  settings in the registry
- prep for 1.0.0 release
- add configurable log_level
- add workaround for some issue where use_redis not properly interpolated in ini


0.5.2 (2023-02-21)
------------------

- bug fix in prince command arg


0.5.1 (2023-02-21)
------------------

- bug fix in 'ready' view


0.5.0 (2023-02-21)
------------------

- allow using redis as data store instead of dbm, optionally
- add/update logging statements
- add pdf_lang additional_arg, default it to "en" (PDF/UA-1 profile in
  prince expects a lang)


0.4.0 (2023-02-01)
------------------

- additional stats kept and displayed
- conversion changes for additional params
- speed up conversion by writing fewer temp files


0.3.1 (2023-01-25)
------------------

- add status/ready endpoint


0.3.0 (2023-01-23)
------------------

- add simple security policy
- upgrade to pyramid 2.0
- update requirements to be generated from `pip-compile` in `pip-tools` and to
  use `requirements.in` as top-level pins


0.2.0 (2023-01-12)
------------------

- upgrade compatibility to princexml 15


0.1
---

-  Upgraded to Python 3.9
-  Added Dockerfile


0.0
---

-  Initial version
