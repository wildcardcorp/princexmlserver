Introduction
============

A simple pyramid server to convert html to PDFs with PrinceXML.


Requirements
------------

- Prince XML installed


Install and Run
---------------

Using git clone:

    virtualenv princeserverenv
    cd princeserverenv
    git clone git@github.com:vangheem/princexmlserver.git
    cd princexmlserver
    ../bin/python setup.py develop
    ../bin/pserve production.ini


Usage
-----

Make post request to <server url>/convert with the follow 
parameters:

xml
    an xml string to convert to the pdf
css
    a json encoded array of css files to use in the pdf generation
doctype
    auto | xml | html | html5(default html)


Example using python requests package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's very simple to use with the requests package:

    import requests
    import json
    requests.post('http://127.0.0.1:6543/convert', data={
        'xml': '<html><body><h1>Foobar</h1></body></html>',
        'css': json.dumps(['h1{color: red}'])
    })
