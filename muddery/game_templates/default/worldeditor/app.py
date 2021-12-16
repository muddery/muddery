"""
ASGI config for websocket project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/

To start the game server you should run the following command in the game directory.
daphne -p 8001 --proxy-headers server.websocket:application
"""

import os
from django.core.asgi import get_asgi_application
from muddery.launcher.manager import setup_editor

# Game directory structure
SETTINGS_DOTPATH = "worldeditor.conf.settings"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_DOTPATH)

setup_editor()

wsgi_application = get_asgi_application()


async def application(scope, receive, send):
    if scope['type'] == 'http':
        # Let Django handle HTTP requests
        await wsgi_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")

