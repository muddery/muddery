"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import url
from muddery.web.webclient import views as webclient_views

urlpatterns = [
    url(r'^$', webclient_views.webclient, name="index"),
    url(r'^', webclient_views.view, name="webclient_view")
]
