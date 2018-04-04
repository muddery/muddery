"""
Decorators of web service controllers.

This decorator can add controllers to the controller dict for future usage.
"""

from __future__ import print_function

import json
from django.conf import settings
from django.http import HttpResponse
from muddery.utils.exception import MudderyError


def request_mapping(func, path=None, key=None):
    """
    A decorator which declears a web service controller.

    Args:
        func: function
        path: (string) request's path
        key: (string) the key of the function
    """
    PROCESSER.add_request_mapping(func, path, key)
        
    def decorate(args):
        return func(args)

    return decorate


class Processer(object):
    """
    HTTP request processer.
    """
    def __init__(self, path_prefix=None):
        if path_prefix:
            if path_prefix[0] != "/":
                path_prefix = "/" + path_prefix

        self.path_prefix = path_prefix
        self.request_dict = {}
        
    def add_request_mapping(self, func, path=None, key=None):
        """
        Declear a web service controller.

        Args:
            path: (string) request's path, begin with "/".
                  If it's empty, use the function's name as the path.
            key: (string) the key of the function
        """
        if path is None:
            path = "/" + func.__name__
        elif not Path:
            path = "/"
        elif path[0] != "/":
            path = "/" + path

        if not key:
            key = ""

        if self.request_dict.has_key((path, key,)):
            raise MudderyError("Request's name duplicated.")

        self.request_dict[(path, key,)] = func

    def response(self, code=0, data=None):
        """
        Generate HTTP response.

	    Args:
    	    code: respond code.
        	data: respond data.
        """
        content = json.dumps({"code": code,
                              "result": data})
        return HttpResponse(content, content_type="application/json")

    def process(self, request):
        """
        Process a request by the func key.
        
        Args:
            request: HTTP request.
        """
        # check authentication
        if not request.user.is_authenticated:
            return self.response(-1, "No permission.")

        path = request.path_info
        if self.path_prefix:
            if path.find(self.path_prefix) == 0:
                path = path[len(self.path_prefix):]
        
        func = request.POST.get("func", "")
        args = request.POST.get("args", None)
        
        print("request: '%s' '%s' '%s'" % (path, func, args))

        if self.request_dict.has_key((path, func,)):
            # call function
            response = self.response(*self.request_dict[(path, func,)](args))
        else:
            response = self.response(1, "Can not find this api.")
        
        return response


PROCESSER = Processer(settings.WORLD_DATA_API_PATH)
