
import json, traceback
from channels.generic.websocket import WebsocketConsumer
from muddery.server.server import Server


class Channel(WebsocketConsumer):
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

    def send_data(self, data_out, close=False):
        """
        Send data to the client.

        :param data_out: data to send {type: data}
        :param close: close connect after sends message.
        """
        # check the data type
        if type(data_out) != str:
            data_out = json.dumps(data_out)

        # send message
        self.send(text_data=data_out, close=close)
