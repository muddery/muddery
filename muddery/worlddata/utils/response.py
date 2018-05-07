"""
Make HTTP response.
"""

from __future__ import print_function

import json
from django.http import HttpResponse, StreamingHttpResponse
from evennia.utils import logger
from muddery.utils.utils import file_iterator


def cross_domain(func):
    """
    A decorator which add cross domain headers.
    """
    def decorate(*args, **kwargs):
        response = func(*args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST,GET,OPTIONS"
        response["Access-Control-Allow-Headers"] = "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type"
        return response
    return decorate


@cross_domain
def success_response(data=None):
    """
    Generate error response.

    Args:
        data: respond data.
    """
    content = json.dumps({"code": 0,
                          "msg": "success",
                          "data": data})
    return HttpResponse(content, content_type="application/json")


@cross_domain
def error_response(code=-1, data=None, msg=None):
    """
    Generate error response.

    Args:
        code: respond code.
        msg: respond mseeage.
        data: respond data.
    """
    content = json.dumps({"code": code,
                          "msg": msg,
                          "data": data})
    return HttpResponse(content, content_type="application/json")


@cross_domain
def file_response(file_obj, filename):
    """
    Respond a file.

    Args:
        file_obj: (file object) file to send.
        filename: (string) filename.
    """
    response = StreamingHttpResponse(file_iterator(file_obj))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % filename
    return response

