"""
All available requests.
"""

from django.conf import settings
from muddery.server.utils.logger import game_editor_logger as logger
from muddery.server.utils.exception import MudderyError
from muddery.server.utils.utils import classes_in_path
from muddery.worldeditor.controllers.base_request_processer import BaseRequestProcesser


class RequestSet(object):
    """
    All available requests.
    """
    def __init__(self):
        self.dict = {}
        self.load()

    def load(self):
        """
        Add all forms from the form path.
        """
        # load classes
        for cls in classes_in_path(settings.PATH_REQUEST_PROCESSERS_BASE, BaseRequestProcesser):
            path = cls.path
            name = cls.name

            if not path and not name:
                logger.log_err("Missing request's path and name.")
                continue

            if path[0] != "/":
                path = "/" + path

            if name is None:
                name = ""

            if (path, name,) in self.dict:
                logger.log_info("Request %s-%s is replaced by %s." % (path, name, cls))

            self.dict[(path, name,)] = cls()

    def get(self, path, name):
        """
        Get the processer responds to the request.
        """
        return self.dict.get((path, name,), None)


REQUEST_SET = RequestSet()

