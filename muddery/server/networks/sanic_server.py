# The sanic server.
import traceback
import asyncio
from sanic import Sanic
from asyncio import CancelledError
from muddery.server.networks.sanic_session import SanicSession
from muddery.server.conf import settings
from muddery.server.server import Server


def run_server():
    async def init_server():
        await Server.inst().connect_db()
        await Server.inst().create_the_world()
        Server.inst().create_command_handler()

    asyncio.run(init_server())

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
            await session.disconnect(0)
        except Exception as e:
            traceback.print_exc()
            await session.disconnect(-1)

        await ws.close()

    server_app.run(port=settings.WEBSERVER_PORT)
