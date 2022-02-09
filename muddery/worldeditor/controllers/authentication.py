"""
Battle commands. They only can be used when a character is in a combat.
"""

from sqlalchemy.orm.exc import NoResultFound
from muddery.server.utils.password import check_password
from muddery.server.utils.exception import MudderyError, ERR
from muddery.worldeditor.utils.auth import generate_token
from muddery.common.networks.responses import success_response
from muddery.worldeditor.controllers.base_request_processer import BaseRequestProcesser
from muddery.worldeditor.dao.accounts import Accounts


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

    def func(self, args):
        if not args or ('username' not in args) or ('password' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        username = args['username']
        raw_password = args['password']

        # Match account name and check password
        try:
            password, salt = Accounts.inst().get_password(username)
        except NoResultFound:
            # Wrong username.
            raise MudderyError(ERR.no_authentication, "Authentication failed.")

        if not check_password(raw_password, password, salt):
            raise MudderyError(ERR.no_authentication, "Authentication failed.")

        token = generate_token()
        Accounts.inst().update_login(username, token)

        return success_response({
            "token": token,
        })


class logout(BaseRequestProcesser):
    """
    Logout the editor.

    Args:
        args: None
    """
    path = "logout"
    name = ""

    def func(self, args):
        """
        Logout the editor.

        Args:
            args: None
        """
        Accounts.inst().set_last_token("")
        return success_response("success")


class query_status(BaseRequestProcesser):
    """
    Get the server's status.

    Args:
        args: None
    """
    path = "status"
    name = ""

    def func(self, args):
        """
        Get the server's status.

        Args:
            args: None
        """
        return success_response("running")
