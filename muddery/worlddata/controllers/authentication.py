"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from django.contrib import auth
from evennia.utils import logger
from muddery.worlddata.services import data_query
from muddery.worlddata.utils import utils
from muddery.utils.exception import MudderyError, ERR
from muddery.worlddata.utils.response import success_response
from muddery.worlddata.controllers.base_request_processer import BaseRequestProcesser


class login(BaseRequestProcesser):
    """
    Login the editor.

    Args:
        args:
            username: username
            password: password
    """
    path = "login"
    name = ""
    login = False
    staff = False

    def func(self, args, request):
        if not args or ('username' not in args) or ('password' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        username = args['username']
        password = args['password']

        user = auth.authenticate(username=username, password=password)
        if not user:
            raise MudderyError(ERR.no_authentication, "Authentication fialed.")

        if not user.is_staff:
            raise MudderyError(ERR.no_permission, "No permission.")

        auth.login(request, user)
        return success_response("success")


class logout(BaseRequestProcesser):
    """
    Logout the editor.

    Args:
        args: None
    """
    path = "logout"
    name = ""

    def func(self, args, request):
        """
        Logout the editor.

        Args:
            args: None
        """
        auth.logout(request)
        return success_response("success")


class query_status(BaseRequestProcesser):
    """
    Get the server's status.

    Args:
        args: None
    """
    path = "status"
    name = ""

    def func(self, args, request):
        """
        Get the server's status.

        Args:
            args: None
        """
        return success_response("running")
