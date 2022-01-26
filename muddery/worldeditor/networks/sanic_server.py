# The sanic server.

import traceback
import os
import signal
import asyncio
from sanic import Sanic
from muddery.server.server import Server as GameServer
from muddery.worldeditor.server import Server as EditorServer
from muddery.worldeditor.settings import SETTINGS
from muddery.server.utils.logger import logger
from muddery.server.utils.utils import write_pid_file, read_pid_file
from muddery.launcher.manager import collect_worldeditor_static


def run():
    pid = read_pid_file(SETTINGS.WORLD_EDITOR_PID)
    if pid:
        print('\nThe worldeditor server has already started.\nYou can run "muddery stop" to stop it and start it again.')
        return

    # run the network
    app = Sanic("muddery_worldeditor")

    @app.before_server_start
    async def before_server_start(app, loop):
        # init the game database
        await GameServer.inst().connect_db()

        # init the worldeditor server
        EditorServer.inst().init()

        # collect static files
        collect_worldeditor_static()

    @app.after_server_start
    async def after_server_start(app, loop):
        # save pid
        write_pid_file(SETTINGS.WORLD_EDITOR_PID, os.getpid())
        print("\nWorldeditor server started.\n")

    @app.after_server_stop
    async def after_server_stop(app, loop):
        # server stopped
        try:
            os.remove(SETTINGS.WORLD_EDITOR_PID)
        except:
            pass
        print("Worldeditor server stopped.")

    # static web pages
    app.static('/editor', SETTINGS.WORLD_EDITOR_WEBROOT)
    app.static('/media', SETTINGS.MEDIA_ROOT)

    # api
    @app.post(SETTINGS.WORLD_EDITOR_API_PATH + "/<func>")
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

    # run the server
    app.run(port=SETTINGS.WORLD_EDITOR_PORT)


def stop():
    # Send a terminate signal to the server.
    pid = read_pid_file(SETTINGS.WORLD_EDITOR_PID)
    if not pid:
        print("Can not get the worldeditor server's pid.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except:
        print("Can not stop the worldeditor server.")
        return

    try:
        os.remove(SETTINGS.WORLD_EDITOR_PID)
    except:
        pass

    print("Worldeditor server stopped.")
