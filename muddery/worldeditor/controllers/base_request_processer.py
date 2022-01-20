"""
Battle commands. They only can be used when a character is in a combat.
"""

from muddery.worldeditor.utils import responses


class BaseRequestProcesser(object):
    """
    Base controller of request controllers.
    """
    path = None
    name = None
    login = True
    staff = True

    def func(self, args):
        return responses.empty_response()
