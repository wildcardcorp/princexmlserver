from pyramid.view import view_config
from js.bootstrap import bootstrap_responsive_css
import json
from princexmlserver.converter import prince
from pyramid.response import Response
from StringIO import StringIO
import time


def _need():
    bootstrap_responsive_css.need()


@view_config(route_name='home', renderer='templates/index.pt')
def my_view(req):
    _need()
    db = req.db
    return {
        'number_converted': db.get('number_converted'),
        'average_time': "%0.2f" % db.get('average_time', 0.0)
    }


def _stats(req, func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    timed = time.time() - start

    db = req.db
    number_converted = db.get('number_converted', 0)
    current_average = db.get('average_time', 0.0)
    current_total = (float(number_converted) * current_average) + timed
    db.put('number_converted', number_converted + 1)
    db.put('average_time', current_total / (float(number_converted) + 1.0))
    return result


@view_config(route_name='convert')
def convert(req):
    """
    Post request variables:
        css: []  # json encoded
        xml: ""
        doctype: auto | xml | html | html5(default html)
    """
    css = json.loads(req.params['css'])
    xml = req.params['xml']
    doctype = req.params.get('doctype', 'html')
    if req.keep_stats:
        pdf = _stats(req, prince.create_pdf, xml, css, doctype)
    else:
        pdf = prince.create_pdf(xml, css, doctype)

    resp = Response(content_type='application/pdf')
    resp.app_iter = StringIO(pdf)
    return resp
