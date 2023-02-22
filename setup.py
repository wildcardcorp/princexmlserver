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

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

requires = [
    'pyramid>=2.0',
    'pyramid-chameleon',
    'waitress',
]

setup(
    name='princexmlserver',
    version='1.0.0.dev0',
    description='princexmlserver',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Pyramid",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Wildcard Corp.',
    author_email='corporate@wildcardcorp.com',
    license='Apache License 2.0',
    url='https://www.wildcardcorp.com',
    keywords='web pyramid princexml',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.9',
    install_requires=requires,
    tests_require=requires,
    extras_require={
        "redis": [ "redis[hiredis]", ],
        "tests": [
            "pytest",
            "pytest-cov",
        ],
    },
    entry_points="""
    [paste.app_factory]
    main = princexmlserver:main
    """)
