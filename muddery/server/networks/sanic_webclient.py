# The sanic server.

import os
import signal
import logging
from sanic import Sanic
from muddery.common.utils.utils import write_pid_file, read_pid_file
from muddery.common.networks import responses
from muddery.launcher.manager import collect_webclient_static
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger


def run(port):
    # Check if a server is running.
    pid = read_pid_file(SETTINGS.WEBCLIENT_PID)
    if pid:
        print('\nThe webclient server has already started.\nYou can run "muddery stop" to stop it and start it again.')
        return

    app = Sanic("muddery_webclient")
    app.static("/", os.path.join(SETTINGS.WEBCLIENT_ROOT, "index.html"))
    app.static("/", SETTINGS.WEBCLIENT_ROOT)
    app.static("/media", SETTINGS.MEDIA_ROOT)

    @app.before_server_start
    async def before_server_start(app, loop):
        # collect static files
        collect_webclient_static()

    @app.after_server_start
    async def after_server_start(app, loop):
        # save pid
        write_pid_file(SETTINGS.WEBCLIENT_PID, os.getpid())
        print("\nWebclient server started.\n")
        logger.log_critical("Webclient server started.")

    @app.after_server_stop
    async def after_server_stop(app, loop):
        # server stopped
        try:
            os.remove(SETTINGS.WEBCLIENT_PID)
        except:
            pass
        print("Webclient server stopped.")
        logger.log_critical("Webclient server stopped.")

    # check the server's status
    @app.get("/status")
    async def get_status(request):
        return responses.success_response()

    if not port:
        port = SETTINGS.WEBSERVER_PORT
    enable_access_log = (SETTINGS.LOG_LEVEL <= logging.INFO)
    app.run(host=SETTINGS.ALLOWED_HOST, port=port, access_log=enable_access_log)


def stop():
    # Send a terminate signal to the server.
    pid = read_pid_file(SETTINGS.WEBCLIENT_PID)
    if not pid:
        print("Can not get the webclient server's pid.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
        print("Webclient server stopped.")
        logger.log_critical("Webclient server killed.")
    except:
        print("Can not stop the webclient server correctly.")

    try:
        os.remove(SETTINGS.WEBCLIENT_PID)
    except:
        pass
