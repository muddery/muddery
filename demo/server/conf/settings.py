"""
Evennia settings file.

The full options are found in the default settings file found here:

C:\GitDir\muddery\evennia\evennia\settings_default.py
C:\GitDir\muddery\muddery\settings_default.py

Note: Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

"""

# Use the defaults from Evennia unless explicitly overridden
import os
from evennia.settings_default import *
from muddery.settings_default import *


######################################################################
# Evennia base server config
######################################################################

# This is a security setting protecting against host poisoning
# attacks.  It defaults to allowing all. In production, make
# sure to change this to your actual host addresses/IPs.
ALLOWED_HOSTS = ['*']

# The webserver sits behind a Portal proxy. This is a list
# of tuples (proxyport,serverport) used. The proxyports are what
# the Portal proxy presents to the world. The serverports are
# the internal ports the proxy uses to forward data to the Server-side
# webserver (these should not be publicly open)
WEBSERVER_PORTS = [(8000, 5001)]

# Server-side websocket port to open for the webclient.
WEBSOCKET_CLIENT_PORT = 8001

# The game server opens an AMP port so that the portal can
# communicate with it.
AMP_PORT = 5000

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
LANGUAGE_CODE = 'zh-cn'


######################################################################
# Django web features
######################################################################

# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies. Do not share this with anyone. Changing it will
# log out all active web browsing sessions. Game web client sessions
# may survive.
SECRET_KEY = '6zP]+lG{[:f,(%7^k5RNJdT0iZcs*>Y.r2}Vm$HI'
