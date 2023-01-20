# The sanic server.

from asyncio import CancelledError
from muddery.common.networks.sanic_server import SanicServer
from muddery.server.networks.sanic_session import SanicSession
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger


class SanicGameServer(SanicServer):
    server_name = SETTINGS.GAME_SERVER_NAME
    host = SETTINGS.ALLOWED_HOST
    port = SETTINGS.GAME_SERVER_PORT

    @classmethod
    def add_routes(cls, app):
        super(SanicGameServer, cls).add_routes(app)

        # set websocket interface
        @app.websocket("/")
        async def handler(request, ws):
            session = SanicSession()
            logger.log_info("[Connection created] %s:%s" % (request.ip, request.port))
            try:
                session.connect(request, ws)
                async for msg in ws:
                    await session.receive(msg)
            except CancelledError as e:
                await session.disconnect(0)
            except Exception as e:
                logger.log_trace("Connection Exception: %s" % e)
                await session.disconnect(-1)

            logger.log_info("[Connection closed] %s:%s" % (request.ip, request.port))
            await ws.close()

    @classmethod
    async def _run_before_server_start(cls, app, loop):
        await super(SanicGameServer, cls)._run_before_server_start(app, loop)

        from muddery.server.server import Server
        await Server.inst().init()
