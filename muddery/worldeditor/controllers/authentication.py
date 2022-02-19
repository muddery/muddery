"""
Battle commands. They only can be used when a character is in a combat.
"""

import base64
from sqlalchemy.orm.exc import NoResultFound
from muddery.common.utils.password import check_password
from muddery.common.utils.exception import MudderyError, ERR
from muddery.common.networks.responses import success_response
from muddery.worldeditor.utils.auth import generate_token
from muddery.worldeditor.utils.crypto import RSA
from muddery.worldeditor.controllers.base_request_processer import BaseRequestProcesser
from muddery.worldeditor.dao.accounts import Accounts
from muddery.worldeditor.settings import SETTINGS


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

    async def func(self, args, request):
        if not args or ('username' not in args) or ('password' not in args):
            raise MudderyError(ERR.missing_args, 'Missing arguments.')

        username = args['username']

        if SETTINGS.ENABLE_ENCRYPT:
            encrypted = base64.b64decode(args["password"])
            decrypted = RSA.inst().decrypt(encrypted)
            raw_password = decrypted.decode("utf-8")
        else:
            raw_password = args["password"]

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

    async def func(self, args, request):
        """
        Logout the editor.

        Args:
            args: None
        """
        Accounts.inst().set_last_token("")
        return success_response("success")
