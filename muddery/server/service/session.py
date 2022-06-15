
import json, traceback
import time
from collections import deque
from muddery.server.server import Server
from muddery.server.utils.logger import logger
from muddery.server.settings import SETTINGS


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

        # Gather all messages send to the client and send them out together.
        self.delay_msg = True

        # Pass messages to the muddery server.
        logger.log_debug("[Receive command][%s]%s" % (self, text_data))

        command_key, args = Server.inst().parse_command(text_data)
        if SETTINGS.SPECIAL_COMMAND_RATE and command_key in SETTINGS.SPECIAL_COMMAND_RATE:
            now = time.time()
            cmd_queue = self.special_command_history[command_key]
            max_rate = SETTINGS.SPECIAL_COMMAND_RATE[command_key]["max_rate"]
            if len(cmd_queue) >= max_rate:
                command_time = cmd_queue.popleft()
                if now - command_time <= 1.0:
                    message = SETTINGS.SPECIAL_COMMAND_RATE[command_key]["message"]
                    await self.msg({"alert": message}, False)
                    return

            cmd_queue.append(now)

        try:
            await Server.inst().handler_command(self, command_key, args)
        except Exception as e:
            logger.log_err("[Receive command][%s]%s error: %s" % (self, text_data, e))

        await self.msg_all()
        self.delay_msg = False

    async def login(self, account):
        """
        Login an account.
        """
        self.authed = True

        if self.account:
            await self.logout()

        self.account = account

        # call hook
        await self.account.at_post_login(self)

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

    async def msg_all(self):
        """
        Send out all messages in the msg_list.
        """
        await self.msg(self.msg_list, delay=False)
        self.msg_list = []

    async def respond_data(self, key: str, data: dict or None = None, delay: bool = True) -> None:
        """
        Respond a request with data.
        """
        await self.msg({
            key: {
                "code": 0,
                "data": data
            }
        }, delay)

    async def respond_err(self, key: str, error_code: int, error_msg: str = "", delay: bool = True) -> None:
        """
        Respond a request with an error message.
        """
        await self.msg({
            key: {
                "code": error_code,
                "msg": error_msg
            }
        }, delay)
