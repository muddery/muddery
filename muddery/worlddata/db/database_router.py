
from __future__ import print_function

from django.conf import settings

DATABASE_MAPPING = settings.DATABASE_APPS_MAPPING

class DatabaseAppsRouter(object):
    """
    A router to control all database operations on models for different
    databases.

    In case an app is not set in settings.DATABASE_APPS_MAPPING, the router
    will fallback to the `default` database.

    Settings example:

    DATABASE_APPS_MAPPING = {'app1': 'db1', 'app2': 'db2'}
    """

    def db_for_read(self, model, **hints):
        """"
        Point all read operations to the specific database.
        """
        return DATABASE_MAPPING.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        """
        Point all write operations to the specific database.
        """
        return DATABASE_MAPPING.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation between apps that use the same database.
        """
        return obj1._meta.app_label == obj2._meta.app_label

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the app only appears in the database.
        """
        return DATABASE_MAPPING.get(app_label, "default") == db
