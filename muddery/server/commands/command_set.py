"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.
"""

from muddery.server.utils.logger import logger
from muddery.common.utils.exception import MudderyError, ERR


class BaseCommandSet(object):
    """
    All user commands are stored in command set.

    Usage:
        @cmdset.command("command's key")
        def func(caller, args):
            "Add a new command function."
            return

        @cmdset.request("request's key")
        def func(caller, args):
            "Add a new request function."
            return result
    """
    _function_set = {}

    @classmethod
    def add(cls, key, func):
        cls._function_set[key] = func

    @classmethod
    def get(cls, key):
        return cls._function_set.get(key)

    @classmethod
    def command(cls, key):
        def wrap(func):
            async def deal_func(caller, args, **kwargs):
                try:
                    await func(caller, args)
                except Exception as e:
                    logger.log_trace("Run command error, %s: %s" % (caller, e))
                    await caller.respond_err("error", "Command %s error: %s" % (key, e))
                    return

            cls.add(key, deal_func)
            return deal_func
        return wrap

    @classmethod
    def request(cls, key):
        def wrap(func):
            async def deal_func(caller, args, **kwargs):
                try:
                    data = await func(caller, args)
                    if not data:
                        data = {}

                    sn = kwargs.get("sn")
                    if sn is not None:
                        caller.msg({
                            "response": {
                                "sn": sn,
                                "code": 0,
                                "data": data
                            }
                        })

                except MudderyError as e:
                    logger.log_trace("Run command error, %s: %s" % (caller, e))
                    sn = kwargs.get("sn")
                    if sn is not None:
                        caller.msg({
                            "response": {
                                "sn": sn,
                                "code": e.code,
                                "data": e.data,
                                "msg": str(e)
                            }
                        })

                    return
                except Exception as e:
                    logger.log_trace("Run command error, %s: %s" % (caller, e))
                    sn = kwargs.get("sn")
                    if sn is not None:
                        caller.msg({
                            "response": {
                                "sn": sn,
                                "code": ERR.unknown,
                                "msg": str(e)
                            }
                        })

                    return

            cls.add(key, deal_func)
            return deal_func
        return wrap


class SessionCmd(BaseCommandSet):
    _function_set = {}


class AccountCmd(BaseCommandSet):
    _function_set = {}


class CharacterCmd(BaseCommandSet):
    _function_set = {}
