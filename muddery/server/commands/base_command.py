"""
The base of all muddery commands.
"""


class BaseCommand(object):
    key = ""

    @classmethod
    async def func(cls, caller, args, context):
        pass
