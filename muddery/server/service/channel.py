
import json, traceback
from muddery.server.server import Server
from muddery.server.utils.logger import logger


class Channel(object):
    """
    Websocket channel.
    """
    def __init__(self, *args, **kwargs):
        """
        Init the channel.

        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.address = None
        self.account = None
        self.authed = False

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
        # Gather all messages send to the client and send them out together.
        self.delay_msg = True

        # Pass messages to the muddery server.
        await Server.inst().handler_message(self, text_data)
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
        Send out a message. To be implemented by a network channel.
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
