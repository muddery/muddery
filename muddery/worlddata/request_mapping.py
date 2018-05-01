"""
All available requests.
"""

from __future__ import print_function

import json
from django.conf import settings
from muddery.utils.exception import MudderyError


def request_mapping(path=None, key=None, login=True, staff=True):
    """
    A decorator which declears a web service controller.

    Args:
        path: (string) request's path.
        key: (string) the key of the function.
        login: (boolean) need login.
        staff: (boolean) for staff only.
    """    
    def wrapper(func):
        """
        Args:
            func: function.
        """
        REQUEST_MAPPING.add_request_mapping(func, path, key, login, staff)

        def decorate(args):
            return func(args)

        return decorate

    return wrapper


class RequestMapping(object):
    """
    All available requests.
    """
    def __init__(self, path_prefix=None):
        if path_prefix:
            if path_prefix[0] != "/":
                path_prefix = "/" + path_prefix

        self.path_prefix = path_prefix
        self.request_dict = {}
        
    def add_request_mapping(self, func, path=None, key=None, login=True, staff=True):
        """
        Declear a web service controller.

        Args:
            path: (string) request's path, begin with "/".
                  If it's empty, use the function's name as the path.
            key: (string) the key of the function.
            login: (boolean) need login.
            staff: (boolean) for staff only.
        """
        if path is None:
            path = "/" + func.__name__
        elif not path:
            path = "/"
        elif path[0] != "/":
            path = "/" + path

        if not key:
            key = ""

        if self.request_dict.has_key((path, key,)):
            raise MudderyError("Request's name duplicated.")

        self.request_dict[(path, key,)] = {
            "func": func,
            "login": login,
            "staff": staff,
        }

    def get_function(self, path, key):
        """
        Get the function responds to the request.
        """
        return self.request_dict.get((path, key,), None)


REQUEST_MAPPING = RequestMapping(settings.WORLD_DATA_API_PATH)

