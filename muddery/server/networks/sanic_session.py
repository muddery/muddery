
import json, traceback
from muddery.server.service.session import Session


class SanicSession(Session):
    """
    Sanic uses websocket's channel as session.
    """
    def __init__(self, *args, **kwargs):
        """
        Init the session.

        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.connection = None

    def connect(self, request, connection):
        """
        Called on a client connecting in.
        """
        # To send message back to the client, accept first.
        self.connection = connection
        self.address = "%s:%s" % (request.ip, request.port)

    async def send_out(self, data: dict or list) -> None:
        """
        Send out message.

        :param data: data to send
        """
        out_text = json.dumps({"data": data}, ensure_ascii=False)

        # send message
        await self.connection.send(out_text)
