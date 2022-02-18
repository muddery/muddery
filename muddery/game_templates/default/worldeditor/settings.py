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

    # http port to open for the worldeditor.
    WORLD_EDITOR_PORT = {WORLD_EDITOR_PORT}

    # The secret key of jwt.
    WORLD_EDITOR_SECRET = "{WORLD_EDITOR_SECRET}"

    # The log level
    LOG_LEVEL = logging.WARNING

    # Also print logs to the console.
    LOG_TO_CONSOLE = False
