import json
import time
from io import BytesIO

from princexmlserver.converter import prince
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/index.pt')
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

def safe_load_param(req, param_key):
    try:
        return json.loads(req.params[param_key])
    except Exception:
        return []

@view_config(route_name='convert')
def convert(req):
    """
    Post request variables:
        css: []  # json encoded
        js: []  # json encoded
        enable_javascript:  # true or false - whether to run js in html file or not
        xml: ""
        doctype: auto | xml | html | html5(default html)
    """
    css = safe_load_param(req, 'css')
    js = safe_load_param(req, 'js')
    xml = req.params['xml']
    doctype = req.params.get('doctype', 'html')
    enable_javascript = req.params.get('enable_javascript', False)
    if req.keep_stats:
        pdf = _stats(
            req,
            prince.create_pdf,
            html=xml,
            css=css,
            js=js,
            doctype=doctype,
            enable_javascript=enable_javascript,
        )
    else:
        pdf = prince.create_pdf(
            html=xml,
            css=css,
            js=js,
            doctype=doctype,
            enable_javascript=enable_javascript,
        )

    resp = Response(content_type='application/pdf')
    resp.app_iter = BytesIO(pdf)
    return resp
