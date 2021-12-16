"""
Battle commands. They only can be used when a character is in a combat.
"""

from django.contrib import auth
from django.contrib.auth.hashers import check_password, is_password_usable, make_password
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from muddery.worldeditor.utils.response import error_response
from muddery.server.utils.exception import MudderyError, ERR
from muddery.worldeditor.utils.response import success_response
from muddery.worldeditor.controllers.base_request_processer import BaseRequestProcesser
from muddery.worldeditor.dao.accounts import Accounts
from muddery.server.utils.localized_strings_handler import _


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

        # Match account name and check password
        user = auth.authenticate(username=username, password=password)
        if not user:
            raise MudderyError(ERR.no_authentication, "Authentication fialed.")

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
