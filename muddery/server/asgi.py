"""
ASGI config for websocket project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import get_default_application
from muddery.launcher.manager import setup as muddery_setup

# Game directory structure
SETTINGS_DOTPATH = "server.conf.settings"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_DOTPATH)
django.setup()
muddery_setup()
application = get_default_application()
