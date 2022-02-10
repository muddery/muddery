"""
Make HTTP response.
"""

from sanic.response import empty, json, ResponseStream
from mimetypes import guess_type


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


def empty_response():
    """
    Empty response.
    """
    return empty()


def success_response(data=None):
    """
    Generate a success response.

    Args:
        data: respond data.
    """
    return json({
        "code": 0,
        "msg": "success",
        "data": data,
    })


def error_response(code=-1, data=None, msg=None, status=400):
    """
    Generate error response.

    Args:
        code: respond code.
        msg: respond message.
        data: respond data.
    """
    return json({
        "code": code,
        "msg": msg,
        "data": data,
    }, status=status)


async def file_response(file_obj, filename):
    """
    Respond a file.

    Args:
        file_obj: (file object) file to send.
        filename: (string) filename.
    """
    async def streaming_fn(response):
        while True:
            content = file_obj.read(4096)
            if len(content) < 1:
                break
            await response.write(content)

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    mime_type = guess_type(filename)[0] or "text/plain"

    return ResponseStream(
        streaming_fn=streaming_fn,
        status=200,
        headers=headers,
        content_type=mime_type,
    )
