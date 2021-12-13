"""
Query and deal common tables.
"""

import importlib
from django.conf import settings
from muddery.worldeditor.dao import general_query_mapper as query
from muddery.server.database.manager import Manager


class ImageResourcesMapper(object):
    """
    Object's image.
    """
    def __init__(self):
        self.model_name = "image_resources"
        session_name = settings.GAME_DATA_APP
        config = settings.AL_DATABASES[session_name]
        module = importlib.import_module(config["MODELS"])
        self.model = getattr(module, self.model_name)
        self.session = Manager.instance().get_session(session_name)

    def get(self, resource):
        """
        Get object's image.

        Args:
            resource: (string) resource's path.
        """
        return query.get_record(self.model_name, resource=resource)

    def add(self, path, type, width, height):
        """
        Add a new image record.

        Args:
            path: image's path
            type: image's type
            width: image's width
            height: image's height

        Return:
            none
        """
        data = {
            "resource": path,
            "type": type,
            "image_width": width,
            "image_height": height,
        }

        record = self.model(**data)
        self.session.add(record)

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise


IMAGE_RESOURCES = ImageResourcesMapper()

