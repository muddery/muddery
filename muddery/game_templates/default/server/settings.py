"""
Game settings file.
"""
import logging


class ServerSettings(object):

    ######################################################################
    # Base server config
    ######################################################################

    # This is a security setting protecting against host poisoning
    # attacks.  It defaults to allowing all. In production, make
    # sure to change this to your actual host addresses/IPs.
    ALLOWED_HOST = "0.0.0.0"

    # The webserver sits behind a Portal proxy.
    WEBCLIENT_PORT = {WEBCLIENT_PORT}

    # Server-side websocket port to open for the webclient.
    GAME_SERVER_PORT = {GAME_SERVER_PORT}

    # The log level
    LOG_LEVEL = logging.WARNING

    # Also print logs to the console.
    LOG_TO_CONSOLE = False
