"""
General helper functions for searching game objects

"""

import traceback
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from muddery.server.database.gamedata.object_keys import OBJECT_KEYS


def get_object_by_key(object_key):
    """
    Search objects by its key.

    Args:
        object_key: (string) object's key.
    """
    object_id = OBJECT_KEYS.get_object_id(object_key)
    if object_id:
        return get_object_by_id(object_id)

    raise ObjectDoesNotExist


def get_object_by_id(object_id):
    """
    Search objects by its id.

    Args:
        object_id: (number) object's id.
    """
    object_db_model = ContentType.objects.get(app_label="objects", model="objectdb").model_class()
    try:
        return object_db_model.objects.get(id=object_id)
    except ObjectDoesNotExist:
        traceback.print_exc()
        print("OBJECT_KEYS.delete(object_id): %s" % object_id)
        OBJECT_KEYS.delete(object_id)

    raise ObjectDoesNotExist
