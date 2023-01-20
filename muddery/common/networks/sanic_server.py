# The sanic server.

import asyncio
import logging
from sanic import Sanic
from sanic.worker.loader import AppLoader
from muddery.common.networks import responses
from muddery.server.settings import SETTINGS
from muddery.server.utils.logger import logger


class SanicServer(object):
    server_name = "Server"
    host = "127.0.0.1"
    port = 8000

    class Listener(object):
        _listeners = {
            "before_server_start": [],
            "after_server_start": [],
            "before_server_stop": [],
            "after_server_stop": [],
        }

        async def run(self, event, *args, **kwargs):
            if event in self._listeners:
                for func in self._listeners[event]:
                    if asyncio.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)

        def before_server_start(self, func):
            self._listeners["before_server_start"].append(func)
            return func

        def after_server_start(self, func):
            self._listeners["after_server_start"].append(func)
            return func

        def before_server_stop(self, func):
            """
            WARNING! This function may not be called when the server stops!

            :param func:
            :return:
            """
            print("WARNING! The before_server_stop function may not be called when the server stops!")
            self._listeners["before_server_stop"].append(func)
            return func

        def after_server_stop(self, func):
            self._listeners["after_server_stop"].append(func)
            return func

    listener = Listener()

    @classmethod
    def creator(cls) -> Sanic:
        app = Sanic(cls.server_name)
        cls.add_statics(app)
        cls.add_routes(app)
        cls.bind_events(app)
        return app

    @classmethod
    def add_statics(cls, app):
        pass

    @classmethod
    def add_routes(cls, app):
        # check the server's status
        @app.get("/state")
        async def get_state(request):
            return responses.success_response()

        @app.get("/terminate")
        async def terminate(request):
            if request.ip != "127.0.0.1":
                # Only can close from local.
                return responses.error_response(status=401)

            async def _terminate():
                app.stop()

            asyncio.create_task(_terminate())
            return responses.success_response()

        @app.get("/restart")
        async def restart(request):
            if request.ip != "127.0.0.1":
                # Only can close from local.
                return

            pass

    @classmethod
    def bind_events(cls, app):
        app.before_server_start(cls._before_server_start)
        app.after_server_start(cls._after_server_start)
        app.before_server_stop(cls._before_server_stop)
        app.after_server_stop(cls._after_server_stop)

    @classmethod
    async def _run_before_server_start(cls, app, loop):
        pass

    @classmethod
    async def _before_server_start(cls, app, loop):
        await cls._run_before_server_start(app, loop)
        await cls.listener.run("before_server_start")

    @classmethod
    async def _run_after_server_start(cls, app, loop):
        print("\n%s started at port %s.\n" % (cls.server_name, cls.port))
        logger.log_critical("%s started." % cls.server_name)

    @classmethod
    async def _after_server_start(cls, app, loop):
        await cls._run_after_server_start(app, loop)
        await cls.listener.run("after_server_start", app, loop)

    @classmethod
    async def _run_before_server_stop(cls, app, loop):
        print("\n%s is stopping.\n" % cls.server_name)
        logger.log_critical("%s is stopping." % cls.server_name)

    @classmethod
    async def _before_server_stop(cls, app, loop):
        """
        WARNING! This function may not be called when the server stops!

        :param app:
        :param loop:
        :return:
        """
        await cls._run_before_server_stop(app, loop)
        await cls.listener.run("before_server_stop", app, loop)

    @classmethod
    async def _run_after_server_stop(cls, app, loop):
        """
        Called after the server stopped.

        :return:
        """
        print("\n%s stopped.\n" % cls.server_name)
        logger.log_critical("%s stopped." % cls.server_name)

    @classmethod
    async def _after_server_stop(cls, app, loop):
        """
        Called after the server stopped.

        :return:
        """
        await cls._run_after_server_stop(app, loop)
        await cls.listener.run("after_server_stop")

    @classmethod
    def init(cls):
        pass

    @classmethod
    def run(cls):
        cls.init()

        enable_log = (SETTINGS.LOG_LEVEL <= logging.INFO)

        loader = AppLoader(factory=cls.creator)
        app = loader.load()
        app.prepare(host=cls.host, port=cls.port, single_process=True, access_log=enable_log, debug=SETTINGS.DEBUG)

        Sanic.serve_single(primary=app)
