
from django.urls import path
from django.core.wsgi import get_wsgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from muddery.server.service.session import Session


wsgi_application = get_wsgi_application()

asgi_application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('', Session.as_asgi()),
        ])
    ),
})

