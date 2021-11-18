
import json
from django.conf import settings
from muddery.server.utils import logger
from muddery.server.utils.utils import class_from_path


def cmdhandler(session, raw_string):
    logger.log_info("Receive command, %s: %s" % (session, raw_string))

    # Parse JSON formated command.
    try:
        data = json.loads(raw_string)
    except Exception:
        # Command is not in JSON, call evennia's cmdparser.
        logger.log_err("Can not parse command, %s: %s" % (session, raw_string))
        return

    command_key = data["cmd"]
    args = data["args"]

    # Find the matching command in cmdset.
    # session commands
    session_cmdset = class_from_path(settings.SESSION_CMDSET)
    command = session_cmdset.get(command_key)
    if command:
        command.func(session, args)
        return

    # account commands
    account = session.account
    if account:
        account_cmdset = class_from_path(settings.ACCOUNT_CMDSET)
        command = account_cmdset.get(command_key)
        if command:
            command.func(account, args)
            return

        # character commands
        character = account.puppet
        if character:
            character_cmdset = class_from_path(settings.CHARACTER_CMDSET)
            command = character_cmdset.get(command_key)
            if command:
                command.func(character, args)
                return

    logger.log_err("Can not find command, %s: %s" % (session, raw_string))