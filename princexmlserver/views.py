from io import BytesIO
import json
import time

from princexmlserver.converter import prince
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='ready')
def ready(req):
    binary = prince._findbinary()
    if binary is None:
        return Response(status_code=500, text='server misconfigured')
    return Response(status_code=200, text='ready')


@view_config(route_name='home', renderer='templates/index.pt', permission='view')
def my_view(req):
    db = req.db
    try:
        return {
            'number_converted': db.get('number_converted'),
            'average_time': "%0.2f" % db.get('average_time', 0.0)
        }
    except ImportError:
        return {
            'number_converted': 0,
            'average_time': '0'
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


@view_config(route_name='convert', permission='view')
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
    resp.app_iter = BytesIO(pdf)
    return resp
