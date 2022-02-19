"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

"""


class CommandSet(object):
    """
    """
    _command_set = {}

    @classmethod
    def create(cls):
        """
        Populates the cmdset
        """
        cls._command_set = {}

    @classmethod
    def add(cls, command):
        cls._command_set[command.key] = command

    @classmethod
    def remove(cls, command):
        del cls._command_set[command.key]

    @classmethod
    def get(cls, command_key):
        return cls._command_set.get(command_key)
