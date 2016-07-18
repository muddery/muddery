"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import *

urlpatterns = [
    url(r'^$', 'muddery.worlddata.views.worldeditor', name="index"),
    url(r'^editor/.*submit.html$', 'muddery.worlddata.views.submit_form', name="submit_form"),
    url(r'^editor/.*form.html$', 'muddery.worlddata.views.view_form', name="view_form"),
    url(r'^editor/.*list.html$', 'muddery.worlddata.views.list_view', name="list_view"),
    url(r'^editor/', 'muddery.worlddata.views.editor', name="editor"),]
