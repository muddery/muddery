# The sanic server.

import os
import signal
from sanic import Sanic
from muddery.server.settings import SETTINGS
from muddery.server.utils.utils import write_pid_file, read_pid_file
from muddery.launcher.manager import collect_webclient_static


def run():
    pid = read_pid_file(SETTINGS.WEBCLIENT_PID)
    if pid:
        print('\nThe webclient server has already started.\nYou can run "muddery stop" to stop it and start it again.')
        return

    app = Sanic("muddery_webclient")
    app.static('/webclient', SETTINGS.WEBCLIENT_ROOT)
    app.static('/media', SETTINGS.MEDIA_ROOT)

    # save pid
    write_pid_file(SETTINGS.WEBCLIENT_PID, os.getpid())

    @app.before_server_start
    async def before_server_start(app, loop):
        # collect static files
        collect_webclient_static()

    @app.after_server_start
    async def after_server_start(app, loop):
        # save pid
        write_pid_file(SETTINGS.WEBCLIENT_PID, os.getpid())
        print("\nWebclient server started.\n")

    @app.after_server_stop
    async def after_server_stop(app, loop):
        # server stopped
        try:
            os.remove(SETTINGS.WEBCLIENT_PID)
        except:
            pass
        print("Webclient stopped.")

    app.run(port=SETTINGS.WEBCLIENT_PORT)


def stop():
    # Send a terminate signal to the server.
    pid = read_pid_file(SETTINGS.WEBCLIENT_PID)
    if not pid:
        print("Can not get the webclient server's pid.")
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except:
        print("Can not stop the webclient server.")
        return

    try:
        os.remove(SETTINGS.WEBCLIENT_PID)
    except:
        pass

    print("Webclient stopped.")
