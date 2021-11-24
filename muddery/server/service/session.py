
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

    def connect(self):
        """
        Called on a client connecting in.
        """
        # To send message back to the client, accept first.
        self.accept()

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
