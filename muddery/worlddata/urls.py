"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import *

urlpatterns = [
    url(r'^$', 'muddery.worlddata.views.worldeditor', name="index"),
    url(r'^editor/submit', 'muddery.worlddata.views.submit_form', name="submit_form"),
    url(r'^editor/view', 'muddery.worlddata.views.view_form', name="view_form"),
    url(r'^editor/', 'muddery.worlddata.views.editor', name="editor"),]
