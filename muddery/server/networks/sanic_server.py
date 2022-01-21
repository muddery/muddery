# The sanic server.
import traceback
import asyncio
from sanic import Sanic
from asyncio import CancelledError
from muddery.server.networks.sanic_channel import SanicChannel
from muddery.server.settings import SETTINGS
from muddery.server.server import Server


def run_server():
    async def init_server():
        await Server.inst().init()

    asyncio.run(init_server())

    server_app = Sanic("muddery_server")

    @server_app.websocket("/")
    async def handler(request, ws):
        channel = SanicChannel()
        try:
            channel.connect(request, ws)
            while True:
                data = await ws.recv()
                await channel.receive(data)
        except CancelledError as e:
            await channel.disconnect(0)
        except Exception as e:
            traceback.print_exc()
            await channel.disconnect(-1)

        await ws.close()

    server_app.run(port=SETTINGS.WEBSERVER_PORT)
