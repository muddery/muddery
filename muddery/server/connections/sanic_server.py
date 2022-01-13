# The sanic server.
import traceback
import asyncio
from sanic import Sanic
from asyncio import CancelledError
from muddery.server.connections.sanic_session import SanicSession
from muddery.server.conf import settings
from muddery.server.server import Server
from muddery.server.database.db_manager import DBManager


async def init_server():
    await Server.inst().connect_db()
    await Server.inst().create_the_world()
    Server.inst().create_command_handler()


loop = asyncio.get_event_loop()
loop.run_until_complete(init_server())
loop.close()


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
