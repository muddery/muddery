"""
This structures the website.

"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include
from django import views as django_views
from muddery.server.web.website import views as website_views

# loop over all settings.INSTALLED_APPS and execute code in
# files named admin.py in each such app (this will add those
# models to the admin site)
admin.autodiscover()

urlpatterns = [
   url(r'^$', website_views.page_index, name="index"),
]
