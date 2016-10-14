"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import url
from muddery.worlddata import views

urlpatterns = [
    url(r'^$', views.worldeditor, name="index"),
    url(r'^editor/.*submit.html$', views.submit_form, name="submit_form"),
    url(r'^editor/.*form.html$', views.view_form, name="view_form"),
    url(r'^editor/.*add.html$', views.add_form, name="add_form"),
    url(r'^editor/.*list.html$', views.list_view, name="list_view"),
    url(r'^editor/.*image.png$', views.get_image, name="image_view"),
    url(r'^editor/', views.editor, name="editor"),]
