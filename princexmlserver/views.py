from datetime import datetime
from io import BytesIO
import json
import logging
from statistics import mean
import time

from princexmlserver.converter import prince
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config


logger = logging.getLogger("princexmlserver")


def _now_formatted():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def _server_status():
    binary = prince._findbinary()
    if binary is None:
        return {
            'status_code': 500,
            'text': 'server misconfigured',
            'class': 'text-danger',
        }
    else:
        return {
            'status_code': 200,
            'text': 'ready',
            'class': 'text-success',
        }


def _stats(req, func, xml, css, additional_args):
    conversion_stat_tags = additional_args.get('conversion_stat_tags', [])
    uuid = additional_args.get('uuid', None)

    conversion_stat_tags.append('all')

    start = time.time()
    result = func(xml, css, additional_args)
    current_elapsed_time = time.time() - start

    db = req.db

    all_conversion_stat_tags = set(json.loads(db.get('conversion_stat_tags', '[]')))
    all_conversion_stat_tags.update(conversion_stat_tags)
    db.put('conversion_stat_tags', json.dumps(list(all_conversion_stat_tags)))

    earliest_stat_date = db.get('earliest_stat_date', None)
    if earliest_stat_date is None:
        db.put('earliest_stat_date', _now_formatted())


    for conversion_stat_tag in all_conversion_stat_tags:
        conversion_count = db.get(f'{conversion_stat_tag}_conversion_count', 0)
        average_conversion_time = db.get(f'{conversion_stat_tag}_average_conversion_time', 0.0)
        longest_conversion_time = db.get(f'{conversion_stat_tag}_longest_conversion_time', 0.0)
        new_total_conversion_time = (float(conversion_count) * average_conversion_time) + current_elapsed_time
        db.put(f'{conversion_stat_tag}_conversion_count', conversion_count + 1)
        db.put(f'{conversion_stat_tag}_average_conversion_time', new_total_conversion_time / (float(conversion_count) + 1.0))
        if current_elapsed_time > longest_conversion_time:
            db.put(f'{conversion_stat_tag}_longest_conversion_time', current_elapsed_time)

        if uuid is not None:
            conversion_counts_by_uuid = json.loads(db.get(f'{conversion_stat_tag}_conversion_counts_by_uuid', '{}'))
            existing_uuid_count = conversion_counts_by_uuid.get(uuid, 0)
            conversion_counts_by_uuid[uuid] = existing_uuid_count + 1
            db.put(f'{conversion_stat_tag}_conversion_counts_by_uuid', json.dumps(conversion_counts_by_uuid))

    return result


@view_config(route_name='ready')
def ready(req):
    server_status = _server_status()
    logger.info(f"reporting status ({server_status['code']}): {server_status['text']}")
    del server_status['class']
    return Response(**server_status)


@view_config(route_name='home', renderer='templates/index.pt', permission='view')
def my_view(req):
    db = req.db
    try:
        earliest_stat_date = db.get('earliest_stat_date', _now_formatted())
        view_data = {
            'stat_rows': [],
            'earliest_stat_date': earliest_stat_date,
            'server_status': _server_status(),
        }
        conversion_stat_tags = json.loads(db.get('conversion_stat_tags', '["all"]'))
        for conversion_stat_tag in conversion_stat_tags:
            count = db.get(f'{conversion_stat_tag}_conversion_count', 0)
            average_conversion_time = db.get(f'{conversion_stat_tag}_average_conversion_time', 0.0)
            longest_conversion_time = db.get(f'{conversion_stat_tag}_longest_conversion_time', 0.0)

            conversion_counts_by_uuid = json.loads(db.get(f'{conversion_stat_tag}_conversion_counts_by_uuid', '{}'))
            conversion_counts = conversion_counts_by_uuid.values()
            if len(conversion_counts):
                average_conversions_per_object = round(mean(conversion_counts), 1)
                max_conversions_per_object = max(conversion_counts)
            else:
                average_conversions_per_object = 'unavailable'
                max_conversions_per_object = 'unavailable'

            view_data['stat_rows'].append({
                'tag_name': conversion_stat_tag,
                'conversion_count': count,
                'average_conversion_time': f'{round(average_conversion_time, 1)} sec',
                'longest_conversion_time': f'{round(longest_conversion_time, 1)} sec',
                'average_conversions_per_object': average_conversions_per_object,
                'max_conversions_per_object': max_conversions_per_object,
            })
        return view_data
    except ImportError:
        return {
            'stat_rows': {
                'tag_name': 'all',
                'conversion_count': 'unavailable',
                'average_conversion_time': 'unavailable',
                'longest_conversion_time': 'unavailable',
                'average_conversions_per_object': 'unavailable',
                'max_conversions_per_object': 'unavailable',
            },
            'earliest_stat_date': _now_formatted(),
            'server_status': _server_status(),
        }


@view_config(route_name='convert', permission='view')
def convert(req):
    """
    Post request variables:
        xml: ""
        css: []  # json encoded
        additional_args: {
            'doctype': auto | xml | html (default)
            'pdf_profile': default 'PDF/UA-1' (see https://www.princexml.com/doc/prince-output/#pdf-versions-and-profiles for options)
            'conversion_stat_tags': [str],
            'uuid': str,
        }
    """
    # this try/except will not throw an error if posted data is not a json string
    # maybe we really want to let this throw the exception instead, and let castle
    # catch and log it, which it's already set up to do
    try:
        data = req.json
    except json.decoder.JSONDecodeError:
        logger.error('problem decoding json', exc_info=True)
        raise HTTPBadRequest("not valid JSON")
    css = data.get('css', [])
    xml = data.get('xml', '')
    additional_args = data.get('additional_args', {})
    if req.keep_stats:
        pdf = _stats(req, prince.create_pdf, xml, css, additional_args)
    else:
        pdf = prince.create_pdf(xml, css, additional_args)

    resp = Response(content_type='application/pdf')
    resp.app_iter = BytesIO(pdf)
    return resp

