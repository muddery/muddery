"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import url
from muddery.worldeditor import views
from muddery.worldeditor import tools

urlpatterns = [
    url(r'^editor/api/', views.editor, name="editor"),]
