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

    # http port to open for the worldeditor.
    WORLD_EDITOR_PORT = 8002
