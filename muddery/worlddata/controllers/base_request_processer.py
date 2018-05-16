"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from muddery.worlddata.utils.response import success_response


class BaseRequestProcesser(object):
    """
    Base controller of request controllers.
    """
    path = None
    name = None
    login = True
    staff = True

    def func(self, args, request):
        return success_response("success")

