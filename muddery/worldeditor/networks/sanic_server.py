# The sanic server.
import traceback
import asyncio
from sanic import Sanic
from muddery.server.server import Server as GameServer
from muddery.worldeditor.server import Server as EditorServer
from muddery.worldeditor.settings import SETTINGS
from muddery.server.utils.logger import logger


def run_server():
    # init server
    async def init_server():
        await GameServer.inst().connect_db()
        EditorServer.inst().init()

    asyncio.run(init_server())

    # run the network
    server_app = Sanic("muddery_worldeditor")

    # static web pages
    server_app.static('/editor', SETTINGS.WORLD_EDITOR_WEBROOT)
    server_app.static('/media', SETTINGS.MEDIA_ROOT)

    # api
    @server_app.post(SETTINGS.WORLD_EDITOR_API_PATH + "/<func>")
    async def handler(request, func):
        token = request.headers.get("Authorization")
        if token:
            token_prefix = "Bearer "
            if token.find(token_prefix) == 0:
                token = token[len(token_prefix):]

        data = request.json if request.method == "POST" else None
        response = EditorServer.inst().handle_request(request.method, request.path, data, token)

        if hasattr(response, "body"):
            print("[RESPOND] '%s' '%s'" % (response.status, response.body))
            logger.log_info("[RESPOND] '%s' '%s'" % (response.status, response.body))
        elif hasattr(response, "streaming_content"):
            logger.log_info("[RESPOND] '%s' streaming_content" % response.status)
        else:
            logger.log_info("[RESPOND] '%s'" % response.status)

        return response

    server_app.run(port=SETTINGS.WORLD_EDITOR_PORT)
