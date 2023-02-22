PrinceXML Server
================

A simple http service that uses [PrinceXML](https://www.princexml.com/) to convert HTML to PDF documents.

**THIS PROJECT IS NOT AFFILIATED WITH [PrinceXML](https://www.princexml.com/)**

This is a free, open-source, python web service that provides an HTTP interface to
the [PrinceXML](https://www.princexml.com) CLI.


## System Requirements

  * PrinceXML (tested with PrinceXML 15)
  * Python 3.9+ (tested with Python 3.9)
  * (optional) Redis

This http service requires [PrinceXML](https://www.princexml.com/) to be installed and accessible to
python in order to function.

It is provided free for use (with a watermark). See [www.princexml.com](https://www.pricnexml.com) for details
on versions, licensing, etc.

PrinceXML Server may make use of Redis if installed and enabled in the application
settings. Redis allows the http service to be used in a multithread/multiprocess
environment.


## Install and Run

Using git clone:

```bash
$ git clone git@github.com:wildcardcorp/princexmlserver.git
$ cd princexmlserver
$ python3 -m venv ./env
$ ./env/bin/python setup.py develop
$ ./env/bin/pserve development.ini
```
### PrinceXML License

If you have a license for [PrinceXML](https://www.princexml.com), you can refer to the documentation
there for how to install it onto the same system you have PrinceXML and the
PrinceXML Server installed onto.

If you are running in a containerized linux environment (eg, using an image
based on the `Dockerfile` in this project), you will, generally,
mount (or copy) the `license.dat` file into `/usr/local/lib/prince/license/`.


## Usage

You can start the service like:

```bash
$ ./env/bin/pserve development.ini
```

And then issue HTTP requests against the `/convert` endpoint, like so:

```bash
$ curl -H 'Content-Type: application/json' \
    -XPOST \
    -d '{"xml":"<html><body>hello</body></html>", "css":["body{background-color:lime}"], "additional_args":{"doctype":"html"}}' \
    -o ./test.pdf
    http://localhost:6543/convert
```

The `/convert` endpoint accepts a JSON document with the following possible
properties (all of which are optional, though leaving out the 'xml' value might
be fruitless):

`xml`
: default `""` -- the text of the document to be converted
`css`
: default [] -- a list of css documents (as strings) to be applied
`additional_args`
: default {} -- a dictionary of additional options for both the service and PrinceXML, such as `doctype`, `pdf_profile`, etc

See `example.py` for an example of how to use the service inside a
Python script that makes use of the `requests` library.


## Pins and dependencies

Dependency pins for the service are primarily tracked in the `requirements.in` file.

To update dependencies, change the relevant pins in `requirements.in`, then compile
it with `pip-compile` from `pip-tools`, eg:

```bash
$ pip install pip-tools
$ pip-compile requirements.in
```

This will produce an updated `requirements.txt` file, which pins every Python dependency
and annotates each dependency with the name of the package(s) that require it's use.
