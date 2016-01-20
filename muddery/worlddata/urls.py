"""
This structures the (simple) structure of the
webpage 'application'.
"""
from django.conf.urls import *

urlpatterns = [
   url(r'^$', 'muddery.worlddata.views.worldeditor', name="index")]
