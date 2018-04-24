"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import url
from muddery.worlddata import views
from muddery.worlddata import tools

urlpatterns = [
    url(r'^editor/api/', views.editor, name="editor"),]
