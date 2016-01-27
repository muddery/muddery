"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import *

urlpatterns = [
    url(r'^$', 'muddery.worlddata.views.worldeditor', name="index"),
    url(r'^editor/', 'muddery.worlddata.views.editor', name="editor")]
