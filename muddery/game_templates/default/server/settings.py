"""
Game settings file.
"""


class ServerSettings(object):

    ######################################################################
    # Base server config
    ######################################################################

    # This is a security setting protecting against host poisoning
    # attacks.  It defaults to allowing all. In production, make
    # sure to change this to your actual host addresses/IPs.
    ALLOWED_HOSTS = "['*']"

    # The webserver sits behind a Portal proxy.
    WEBCLIENT_PORT = {WEBCLIENT_PORT}

    # Server-side websocket port to open for the webclient.
    GAME_SERVER_PORT = {GAME_SERVER_PORT}

    # The secret key of jwt.
    WORLD_EDITOR_SECRET = "SET_YOUR_SECRET_KEY"
