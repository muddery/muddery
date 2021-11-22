"""
The base of all muddery commands.
"""


class BaseCommand(object):
    key = ""

    @classmethod
    def func(cls, caller, args, context):
        pass
