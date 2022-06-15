"""
The base of all muddery commands.
"""

from muddery.server.utils.logger import logger
from muddery.common.utils.exception import MudderyError


class BaseCommand(object):
    """
    The base class to deal with user commands.
    """
    key = ""

    @classmethod
    async def process(cls, caller, args):
        try:
            await cls.func(caller, args)
        except Exception as e:
            logger.log_err("Run command error, %s: %s" % (caller, e))
            await caller.respond_err("error", "Command %s error: %s" % (cls.key, e))
            return

    @classmethod
    async def func(cls, caller, args):
        pass


class BaseRequest(BaseCommand):
    """
    The base class to deal with client requests.
    All requests must be respond.
    """
    key = ""

    @classmethod
    async def process(cls, caller, args):
        try:
            result = await cls.func(caller, args)
        except MudderyError as e:
            await caller.respond_err(cls.key, e.code, str(e))
            return
        except Exception as e:
            logger.log_err("Run command error, %s: %s" % (caller, e))
            await caller.respond_err("error", "Command %s error: %s" % (cls.key, e))
            return

        await caller.respond_data(cls.key, result)
