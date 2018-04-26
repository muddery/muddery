"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.conf import settings
from evennia.utils import logger
from django.contrib import auth
from muddery.worlddata.request_mapping import request_mapping
from muddery.worlddata.service import data_query
from muddery.worlddata.utils import utils
from muddery.utils.exception import MudderyError


@request_mapping(login=False)
def login(args, request):
    """
    Login the editor.

    Args:
        args:
            username: username
            password: password
    """
    if not args or ('username' not in args) or ('password' not in args):
        raise MudderyError(10000, 'Missing arguments.')

    username = args['username']
    password = args['password']

    user = auth.authenticate(username=username, password=password)
    if user:
        auth.login(request, user)
        return "success"

    raise MudderyError(10001, "Authentication fialed.")


@request_mapping
def logout(args, request):
    """
    Logout the editor.

    Args:
        args: None
    """
    auth.logout(request)

