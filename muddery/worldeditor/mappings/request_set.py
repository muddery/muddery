"""
All available requests.
"""

from muddery.common.utils.utils import classes_in_path
from muddery.worldeditor.utils.logger import logger
from muddery.worldeditor.settings import SETTINGS
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
        for cls in classes_in_path(SETTINGS.PATH_REQUEST_PROCESSERS_BASE, BaseRequestProcesser):
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
