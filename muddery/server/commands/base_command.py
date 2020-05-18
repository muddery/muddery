"""
The base of all muddery commands.
"""

import json
from evennia.commands.command import Command


class BaseCommand(Command):
    def __init__(self, *warg, **kwargs):
        super(BaseCommand, self).__init__(*warg, **kwargs)

        self.context = None

    def parse(self):
        """
        parse command args
        """
        try:
            # Get context.
            data = json.loads(self.raw_string)
            self.context = data["context"]
        except Exception as e:
            pass
