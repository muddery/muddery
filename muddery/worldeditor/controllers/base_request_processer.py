"""
Battle commands. They only can be used when a character is in a combat.
"""

from muddery.common.networks import responses


class BaseRequestProcesser(object):
    """
    Base controller of request controllers.
    """
    path = None
    name = None
    login = True
    staff = True

    async def func(self, args, request):
        return responses.empty_response()
