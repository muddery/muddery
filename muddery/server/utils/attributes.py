"""
Attributes are arbitrary data stored on objects. Attributes supports
both pure-string values and pickled arbitrary data.

Attributes are also used to implement Nicks. This module also contains
the Attribute- and NickHandlers as well as the `NAttributeHandler`,
which is a non-db version of Attributes.


"""
import re
import fnmatch
import weakref

from django.apps import apps
from django.conf import settings

from evennia.utils.dbserialize import to_pickle, from_pickle
from evennia.utils.utils import lazy_property, to_str, make_iter, is_iter


# -------------------------------------------------------------
#
#   Attributes
#
# -------------------------------------------------------------

#
# Handlers making use of the Attribute model
#

class AttributeHandler(object):
    """
    Handler for adding Attributes to the object.
    """

    def __init__(self, obj):
        """Initialize handler."""
        self.obj_id = obj.id
        self.model_obj = apps.get_model(settings.GAME_DATA_APP, "object_attributes")

    def has(self, key):
        """
        Checks if the given Attribute exists on the object.

        Args:
            key (str): The Attribute key to check for.

        Returns:
            has_attribute (bool): If the Attribute exists on this object or not.
        """
        records = self.model_obj.objects.filter(obj_id=self.obj_id, key=key)
        return len(records) > 0

    def get(self, key):
        """
        Get the Attribute.

        Args:
            key (str): the attribute identifier.

        Returns:
            result (any): The value matches the key.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key`.

        """
        records = self.model_obj.objects.filter(obj_id=self.obj_id, key=key)
        if len(records) == 0:
            raise AttributeError
        else:
            return records[0].value

    def add(
        self,
        key,
        value,
        category=None,
        lockstring="",
        strattr=False,
        accessing_obj=None,
        default_access=True,
    ):
        """
        Add attribute to object, with optional `lockstring`.

        Args:
            key (str): An Attribute name to add.
            value (any or str): The value of the Attribute. If
                `strattr` keyword is set, this *must* be a string.
            category (str, optional): The category for the Attribute.
                The default `None` is the normal category used.
            lockstring (str, optional): A lock string limiting access
                to the attribute.
            strattr (bool, optional): Make this a string-only Attribute.
                This is only ever useful for optimization purposes.
            accessing_obj (object, optional): An entity to check for
                the `attrcreate` access-type. If not passing, this method
                will be exited.
            default_access (bool, optional): What access to grant if
                `accessing_obj` is given but no lock of the type
                `attrcreate` is defined on the Attribute in question.

        """
        if accessing_obj and not self.obj.access(
            accessing_obj, self._attrcreate, default=default_access
        ):
            # check create access
            return

        if not key:
            return

        category = category.strip().lower() if category is not None else None
        keystr = key.strip().lower()
        attr_obj = self._getcache(key, category)

        if attr_obj:
            # update an existing attribute object
            attr_obj = attr_obj[0]
            if strattr:
                # store as a simple string (will not notify OOB handlers)
                attr_obj.db_strvalue = value
                attr_obj.save(update_fields=["db_strvalue"])
            else:
                # store normally (this will also notify OOB handlers)
                attr_obj.value = value
        else:
            # create a new Attribute (no OOB handlers can be notified)
            kwargs = {
                "db_key": keystr,
                "db_category": category,
                "db_model": self._model,
                "db_attrtype": self._attrtype,
                "db_value": None if strattr else to_pickle(value),
                "db_strvalue": value if strattr else None,
            }
            new_attr = Attribute(**kwargs)
            new_attr.save()
            getattr(self.obj, self._m2m_fieldname).add(new_attr)
            # update cache
            self._setcache(keystr, category, new_attr)

    def remove(
        self,
        key=None,
        raise_exception=False,
        category=None,
        accessing_obj=None,
        default_access=True,
    ):
        """
        Remove attribute or a list of attributes from object.

        Args:
            key (str or list, optional): An Attribute key to remove or a list of keys. If
                multiple keys, they must all be of the same `category`. If None and
                category is not given, remove all Attributes.
            raise_exception (bool, optional): If set, not finding the
                Attribute to delete will raise an exception instead of
                just quietly failing.
            category (str, optional): The category within which to
                remove the Attribute.
            accessing_obj (object, optional): An object to check
                against the `attredit` lock. If not given, the check will
                be skipped.
            default_access (bool, optional): The fallback access to
                grant if `accessing_obj` is given but there is no
                `attredit` lock set on the Attribute in question.

        Raises:
            AttributeError: If `raise_exception` is set and no matching Attribute
                was found matching `key`.

        Notes:
            If neither key nor category is given, this acts as clear().

        """

        if key is None:
            self.clear(
                category=category, accessing_obj=accessing_obj, default_access=default_access
            )
            return

        category = category.strip().lower() if category is not None else None

        for keystr in make_iter(key):
            keystr = keystr.lower()

            attr_objs = self._getcache(keystr, category)
            for attr_obj in attr_objs:
                if not (
                    accessing_obj
                    and not attr_obj.access(accessing_obj, self._attredit, default=default_access)
                ):
                    try:
                        attr_obj.delete()
                    except AssertionError:
                        print("Assertionerror for attr.delete()")
                        # this happens if the attr was already deleted
                        pass
                    finally:
                        self._delcache(keystr, category)
            if not attr_objs and raise_exception:
                raise AttributeError

    def clear(self, category=None, accessing_obj=None, default_access=True):
        """
        Remove all Attributes on this object.

        Args:
            category (str, optional): If given, clear only Attributes
                of this category.
            accessing_obj (object, optional): If given, check the
                `attredit` lock on each Attribute before continuing.
            default_access (bool, optional): Use this permission as
                fallback if `access_obj` is given but there is no lock of
                type `attredit` on the Attribute in question.

        """
        category = category.strip().lower() if category is not None else None

        if not self._cache_complete:
            self._fullcache()

        if category is not None:
            attrs = [attr for attr in self._cache.values() if attr.category == category]
        else:
            attrs = self._cache.values()

        if accessing_obj:
            [
                attr.delete()
                for attr in attrs
                if attr and attr.access(accessing_obj, self._attredit, default=default_access)
            ]
        else:
            [attr.delete() for attr in attrs if attr and attr.pk]
        self._cache = {}
        self._catcache = {}
        self._cache_complete = False

    def all(self, accessing_obj=None, default_access=True):
        """
        Return all Attribute objects on this object, regardless of category.

        Args:
            accessing_obj (object, optional): Check the `attrread`
                lock on each attribute before returning them. If not
                given, this check is skipped.
            default_access (bool, optional): Use this permission as a
                fallback if `accessing_obj` is given but one or more
                Attributes has no lock of type `attrread` defined on them.

        Returns:
            Attributes (list): All the Attribute objects (note: Not
                their values!) in the handler.

        """
        if _TYPECLASS_AGGRESSIVE_CACHE:
            if not self._cache_complete:
                self._fullcache()
            attrs = sorted([attr for attr in self._cache.values() if attr], key=lambda o: o.id)
        else:
            attrs = sorted([attr for attr in self._query_all() if attr], key=lambda o: o.id)

        if accessing_obj:
            return [
                attr
                for attr in attrs
                if attr.access(accessing_obj, self._attredit, default=default_access)
            ]
        else:
            return attrs
