
import json, traceback
import time
from collections import deque
from muddery.common.utils.exception import MudderyError, ERR
from muddery.server.utils.logger import logger
from muddery.server.settings import SETTINGS
from muddery.server.commands.command_set import SessionCmd, AccountCmd, CharacterCmd


class Session(object):
    """
    Communicate session.
    """
    def __init__(self, *args, **kwargs):
        """
        Init the session.

        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.address = None
        self.account = None
        self.authed = False

        self.command_history = deque()
        self.special_command_history = None
        if SETTINGS.SPECIAL_COMMAND_RATE:
            self.special_command_history = {key: deque() for key in SETTINGS.SPECIAL_COMMAND_RATE}

        self.msg_list = []
        self.delay_msg = False

    def __str__(self):
        """
        Output self as a string
        """
        output = self.address
        if self.account:
            output += "-" + str(self.account)
        return output

    async def disconnect(self, close_code):
        """
        Called on a client disconnected.
        """
        if self.account:
            await self.logout()

    async def receive(self, text_data=None, bytes_data=None):
        """
        Received a message from the client.

        :param text_data:
        :param bytes_data:
        :return:
        """
        if SETTINGS.MAX_COMMAND_RATE:
            now = time.time()
            if len(self.command_history) >= SETTINGS.MAX_COMMAND_RATE:
                command_time = self.command_history.popleft()
                if now - command_time <= 1.0:
                    await self.msg({"alert": SETTINGS.COMMAND_RATE_WARNING}, False)
                    return

            self.command_history.append(now)

        # Pass messages to the muddery server.
        logger.log_debug("[Receive command][%s]%s" % (self, text_data))

        data = json.loads(text_data)
        command = data["cmd"] if "cmd" in data else None
        args = data["args"] if "args" in data else None
        serial_number = data["sn"] if "sn" in data else None

        if not command:
            logger.log_err("Can not find command.")
            if serial_number:
                await self.msg({
                    "response": {
                        "sn": serial_number,
                        "code": ERR.can_not_find_command,
                        "msg": "Can not find command: %s" % command
                    }
                }, False)
            return

        # get session commands
        caller = self
        func = SessionCmd.get(command)
        if not func:
            caller = self.account
            if caller:
                # get account command
                func = AccountCmd.get(command)
                if not func:
                    caller = self.account.get_puppet_obj()
                    if caller:
                        # get character command
                        func = CharacterCmd.get(command)

        if not func:
            logger.log_err("Can not find command, %s: %s" % (self, command))
            if serial_number:
                await self.msg({
                    "response": {
                        "sn": serial_number,
                        "code": ERR.can_not_find_command,
                        "msg": "Can not find command: %s" % command
                    }
                }, False)
            return

        await func(caller, args, sn=serial_number)

        if self.msg_list:
            await self.msg(self.msg_list, False)
            self.msg_list = []

    async def login(self, account) -> dict:
        """
        Login an account.
        """
        self.authed = True

        if self.account:
            await self.logout()

        self.account = account

        # call hook
        return await self.account.login(self)

    async def logout(self):
        """
        Logout an account
        """
        if self.account:
            # call hook
            await self.account.at_pre_logout()

        self.account = None
        self.authed = False

    async def send_out(self, data: dict or list) -> None:
        """
        Send out a message. To be implemented by the network.
        """
        pass

    async def msg(self, data: dict or list, delay: bool = True) -> None:
        """
        Send data to the client.

        :param data: data to send
        :param delay: delay sending out messages when self.delay_msg is set.
        """
        if self.delay_msg and delay:
            # Delay sending out messages when self.delay_msg is set.
            if type(data) == list:
                self.msg_list.extend(data)
            else:
                self.msg_list.append(data)
        else:
            # Send out this message immediately.
            logger.log_debug("[Send message][%s]%s" % (self, data))

            # send message
            try:
                await self.send_out(data)
            except Exception as e:
                logger.log_err("[Send message error][%s]%s" % (self, e))
