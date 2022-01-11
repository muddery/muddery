# The sanic server.
import traceback

from sanic import Sanic
from asyncio import CancelledError
from muddery.server.connections.sanic_session import SanicSession
from muddery.server.conf import settings
from muddery.server.server import Server


Server.inst()


server_app = Sanic("muddery_server")


@server_app.websocket("/")
async def handler(request, ws):
    session = SanicSession()
    try:
        session.connect(request, ws)
        while True:
            data = await ws.recv()
            await session.receive(data)
    except CancelledError as e:
        pass
    except Exception as e:
        traceback.print_exc()

    session.disconnect(0)
