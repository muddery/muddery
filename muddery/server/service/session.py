
import json, traceback
from channels.generic.websocket import WebsocketConsumer
from muddery.server.server import Server


class Session(WebsocketConsumer):
    """
    Websocket path.
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

    def __str__(self):
        """
        Output self as a string
        """
        output = self.address
        if self.account:
            output += "-" + str(self.account)
        return output

    def connect(self):
        """
        Called on a client connecting in.
        """
        # To send message back to the client, accept first.
        self.accept()
        self.address = "%s:%s" % (self.scope["client"][0], self.scope["client"][1])

    def disconnect(self, close_code):
        """
        Called on a client disconnected.
        """
        pass

    def receive(self, text_data=None, bytes_data=None):
        """
        Received a message from the client.

        :param text_data:
        :param bytes_data:
        :return:
        """
        # Pass messages to the muddery server.
        Server.instance().handler_message(self, text_data)

    def login(self, account):
        """
        Login an account.
        """
        self.authed = True

        if self.account:
            self.logout()

        self.account = account

        # call hook
        self.account.at_post_login(self)

    def logout(self):
        """
        Logout an account
        """
        if self.account:
            # call hook
            self.account.at_pre_logout(self)

        self.account = None
        self.authed = False

    def msg(self, text, context=None):
        """
        Send data to the client.

        :param data_out: data to send {type: data}
        :param close: close connect after sends message.
        """
        # create the output string
        out_text = json.dumps({"data": text, "context": context}, ensure_ascii=False)

        # send message
        self.send(text_data=out_text, close=False)
