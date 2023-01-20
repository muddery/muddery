# The sanic server.

import os
import json
from muddery.common.networks.sanic_server import SanicServer
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.utils.logger import logger


class SanicWorldEditor(SanicServer):
    server_name = SETTINGS.WORLD_EDITOR_SERVER_NAME
    host = SETTINGS.ALLOWED_HOST
    port = SETTINGS.WORLD_EDITOR_PORT

    @classmethod
    def add_statics(cls, app):
        super(SanicWorldEditor, cls).add_statics(app)

        # static web pages
        app.static("/", os.path.join(SETTINGS.WORLD_EDITOR_WEBROOT, "index.html"), name="index")
        app.static("/", SETTINGS.WORLD_EDITOR_WEBROOT, name="root")
        app.static("/media", SETTINGS.MEDIA_ROOT, name="media")

    @classmethod
    def add_routes(cls, app):
        super(SanicWorldEditor, cls).add_routes(app)

        from muddery.worldeditor.server import Server

        # api
        @app.post(SETTINGS.WORLD_EDITOR_API_PATH + "/<func>")
        async def api_handler(request, func):
            token = request.headers.get("Authorization")
            if token:
                token_prefix = "Bearer "
                if token.find(token_prefix) == 0:
                    token = token[len(token_prefix):]

            data = None
            if request.content_type == "application/json":
                data = request.json
            elif request.content_type == "application/x-www-form-urlencoded":
                data = {}
                if "func_no" in request.form and len(request.form["func_no"]) > 0:
                    data["func_no"] = json.loads(request.form["func_no"][0])
                if "args" in request.form and len(request.form["args"]) > 0:
                    data["args"] = json.loads(request.form["args"][0])
                if "token" in request.form and len(request.form["token"]) > 0:
                    token = request.form["token"][0]
            elif request.content_type.index("multipart/form-data;") == 0:
                data = request.form

            if not data:
                data = {}

            response = await Server.inst().handle_request(request.method, func, data, request, token)

            if hasattr(response, "body"):
                logger.log_debug("[RESPOND] '%s' '%s'" % (response.status, response.body))
            elif hasattr(response, "streaming_content"):
                logger.log_debug("[RESPOND] '%s' streaming_content" % response.status)
            else:
                logger.log_debug("[RESPOND] '%s'" % response.status)

            return response

        # upload files
        @app.post(SETTINGS.WORLD_EDITOR_UPLOAD_PATH + "/<func>")
        async def upload_handler(request, func):
            token = request.headers.get("Authorization")
            if token:
                token_prefix = "Bearer "
                if token.find(token_prefix) == 0:
                    token = token[len(token_prefix):]

            data = None
            if request.content_type == "application/json":
                data = request.json
            elif request.content_type.index("multipart/form-data;") == 0:
                data = {}
                if "func_no" in request.form and len(request.form["func_no"]) > 0:
                    data["func_no"] = json.loads(request.form["func_no"][0])
                if "args" in request.form and len(request.form["args"]) > 0:
                    data["args"] = json.loads(request.form["args"][0])

            if not data:
                data = {}

            response = await Server.inst().handle_request(request.method, func, data, request, token)

            if hasattr(response, "body"):
                logger.log_debug("[RESPOND] '%s' '%s'" % (response.status, response.body))
            elif hasattr(response, "streaming_content"):
                logger.log_debug("[RESPOND] '%s' streaming_content" % response.status)
            else:
                logger.log_debug("[RESPOND] '%s'" % response.status)

            return response

    @classmethod
    async def _run_before_server_start(cls, app, loop):
        await super(SanicWorldEditor, cls)._run_before_server_start(app, loop)

        # init the world editor server
        from muddery.worldeditor.server import Server
        Server.inst().init()

        # collect static files
        from muddery.launcher.manager import collect_worldeditor_static
        collect_worldeditor_static()
