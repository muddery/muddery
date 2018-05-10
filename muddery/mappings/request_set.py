"""
All available requests.
"""

from __future__ import print_function

from django.conf import settings
from muddery.utils.exception import MudderyError


def request_mapping(*args, **kwargs):
    """
    A decorator which declears a web service controller.

    Args:
        path: (string) request's path.
        key: (string) the key of the function.
        login: (boolean) need login.
        staff: (boolean) for staff only.
    """
    if args:
        func = args[0]
        REQUEST_SET.add(*args)
        return func

    else:
        path = kwargs.get("path", None)
        key = kwargs.get("key", None)
        login = kwargs.get("login", True)
        staff = kwargs.get("staff", True)
        
        def wrapper(func):
            """
            Args:
                func: function.
            """
            REQUEST_SET.add(func, path, key, login, staff)
            return func
        return wrapper


class RequestSet(object):
    """
    All available requests.
    """
    def __init__(self, path_prefix=None):
        if path_prefix:
            if path_prefix[0] != "/":
                path_prefix = "/" + path_prefix

        self.path_prefix = path_prefix
        self.dict = {}
        
    def add(self, func, path=None, key=None, login=True, staff=True):
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

        if not path and not key:
            raise MudderyError("Missing request's path and key.")

        if not key:
            key = ""

        if self.dict.has_key((path, key,)):
            raise MudderyError("Request's name duplicated.")

        self.dict[(path, key,)] = {
            "func": func,
            "login": login,
            "staff": staff,
        }

    def get(self, path, key):
        """
        Get the function responds to the request.
        """
        return self.dict.get((path, key,), None)


REQUEST_SET = RequestSet(settings.WORLD_DATA_API_PATH)

