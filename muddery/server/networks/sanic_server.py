# The sanic server.

import traceback
import logging
import os
import signal
from sanic import Sanic
from asyncio import CancelledError
from muddery.server.networks.sanic_channel import SanicChannel
from muddery.server.settings import SETTINGS
from muddery.server.server import Server
from muddery.server.utils.utils import write_pid_file, read_pid_file
from muddery.worldeditor.utils import responses


def run():
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

    @app.after_server_stop
    async def after_server_stop(app, loop):
        # server stopped
        try:
            os.remove(SETTINGS.SERVER_PID)
        except:
            pass
        print("Game server stopped.")

    # check the server's status
    @app.get("/status")
    async def get_status(request):
        return responses.success_response()

    # set websocket interface
    @app.websocket("/")
    async def handler(request, ws):
        channel = SanicChannel()
        print("[Connection created] %s:%s" % (request.ip, request.port))
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

        print("[Connection closed] %s:%s" % (request.ip, request.port))
        await ws.close()

    # run the server
    app.run(port=SETTINGS.WEBSERVER_PORT)


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
