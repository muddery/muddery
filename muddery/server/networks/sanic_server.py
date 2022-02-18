# The sanic server.

import traceback
import os
import signal
import logging
from sanic import Sanic
from asyncio import CancelledError
from muddery.common.utils.utils import write_pid_file, read_pid_file
from muddery.common.networks import responses
from muddery.server.networks.sanic_channel import SanicChannel
from muddery.server.settings import SETTINGS
from muddery.server.server import Server
from muddery.server.utils.logger import logger


def run(port):
    # Check if a server is running.
    pid = read_pid_file(SETTINGS.SERVER_PID)
    if pid:
        print('\nThe game server has already started.\nYou can run "muddery stop" to stop it and start it again.')
        return

    app = Sanic("muddery_server")

    @app.before_server_start
    async def before_server_start(app, loop):
        # init the game server
        await Server.inst().init()

    @app.after_server_start
    async def after_server_start(app, loop):
        # save pid
        write_pid_file(SETTINGS.SERVER_PID, os.getpid())
        print("\nGame server server started.\n")
        logger.log_critical("Game server server started.")

    @app.after_server_stop
    async def after_server_stop(app, loop):
        # server stopped
        try:
            os.remove(SETTINGS.SERVER_PID)
        except:
            pass
        print("Game server stopped.")
        logger.log_critical("Game server stopped.")

    # check the server's status
    @app.get("/status")
    async def get_status(request):
        return responses.success_response()

    # set websocket interface
    @app.websocket("/")
    async def handler(request, ws):
        channel = SanicChannel()
        logger.log_info("[Connection created] %s:%s" % (request.ip, request.port))
        try:
            channel.connect(request, ws)
            while True:
                data = await ws.recv()
                await channel.receive(data)
        except CancelledError as e:
            await channel.disconnect(0)
        except Exception as e:
            logger.log_trace("Connection Exception: %s" % e)
            await channel.disconnect(-1)

        logger.log_info("[Connection closed] %s:%s" % (request.ip, request.port))
        await ws.close()

    # run the server
    if not port:
        port = SETTINGS.WEBSERVER_PORT
    enable_access_log = (SETTINGS.LOG_LEVEL <= logging.INFO)
    app.run(host=SETTINGS.ALLOWED_HOST, port=port, access_log=enable_access_log)


def stop():
    # Send a terminate signal to the server.
    pid = read_pid_file(SETTINGS.SERVER_PID)
    if not pid:
        print("Can not get the game server's pid.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
        print("Game server stopped.")
    except:
        print("Can not stop the game server correctly.")

    try:
        os.remove(SETTINGS.SERVER_PID)
    except:
        pass
