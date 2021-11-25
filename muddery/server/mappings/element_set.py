"""
All available requests.
"""

import os, re
from importlib import import_module
from django.conf import settings
from muddery.server.utils.logger import game_server_logger as logger
from muddery.server.utils.utils import class_from_path
from muddery.server.utils.utils import get_module_path


class ElementSet(object):
    """
    All available classes.
    """
    def __init__(self):
        self.module_dict = {}
        self.class_dict = {}

        self.all_loaded = False
        self.match_class = re.compile(r'^class\s+(\w+)\s*.*$')
        self.match_key = re.compile(r""" {4}element_type\s*=\s*("|')(.+)("|')\s*$""")

    def load_files(self, component_path):
        """
        Get elements' file path.
        """
        if not component_path:
            return

        module = import_module(component_path)
        base_path = module.__path__
        if not base_path:
            return

        base_path = base_path[0]
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext != ".py":
                    continue

                with open(os.path.join(root, filename), "r", encoding="utf-8") as fp:
                    class_name = ""
                    for line in fp.readlines():
                        if not class_name:
                            match = self.match_class.match(line)
                            if match:
                                class_name = match.group(1)
                        else:
                            match = self.match_key.match(line)
                            if match:
                                key_name = match.group(2)

                                module_path = component_path
                                if base_path == root:
                                    module_path += "." + name + "." + class_name
                                else:
                                    relative_path = get_module_path(os.path.relpath(root, base_path))
                                    module_path += "." + relative_path + "." + name + "." + class_name

                                if key_name in self.module_dict:
                                    logger.log_info("Element %s is replaced by %s." % (key_name, module_path))

                                self.module_dict[key_name] = module_path
                                class_name = ""

    def load_classes(self):
        """
        Add all elements from the element_type path.

        To prevent loop import, call this method later.
        """
        if self.all_loaded:
            return

        for key in self.module_dict:
            if key in self.class_dict:
                continue
            cls = class_from_path(self.module_dict[key])
            self.class_dict[key] = cls

        self.all_loaded = True

    def get(self, key):
        """
        Get a element_type recursively.
        """
        if key in self.class_dict:
            return self.class_dict[key]
        elif key in self.module_dict:
            cls = class_from_path(self.module_dict[key])
            if key in self.class_dict:
                if self.class_dict[key] != cls:
                    logger.log_info("Element %s is replaced by %s." % (key, cls))

            self.class_dict[key] = cls
            return cls

        logger.log_err("Can not find element type: %s." % key)

    def get_module(self, key):
        """
        Get a element_type's module path.
        """
        return self.module_dict.get(key, None)

    def get_group(self, group_key):
        """
        Get a element_type and its all children.
        """
        self.load_classes()

        cls = self.class_dict[group_key]
        element_types = {group_key: cls}

        for key in self.class_dict:
            if issubclass(self.class_dict[key], cls):
                element_types[key] = self.class_dict[key]

        return element_types

    def get_class_models(self, key):
        """
        Get an element type's models.
        """
        cls = self.get(key)
        if cls:
            return cls.get_models()
        else:
            return []

    def get_all_info(self):
        """
        Get all element type's information.

        Return: (dict) all element type's information.
        """
        self.load_classes()

        info = {}
        for key, cls in self.class_dict.items():
            # Get the class's parent which has another element name.
            bases = cls.__bases__
            parent_type = ""
            while not parent_type:
                has_element_type = False
                for base in bases:
                    if hasattr(base, "element_type") and base.element_type:
                        has_element_type = True

                        if base.element_type != cls.element_type:
                            parent_type = base.element_type
                        else:
                            bases = base.__bases__
                        break

                if not has_element_type:
                    break

            info[key] = {
                "name": cls.element_name,
                "parent": parent_type
            }

        return info


ELEMENT_SET = ElementSet()
ELEMENT = ELEMENT_SET.get
ELEMENT_SET.load_files(settings.PATH_ELEMENTS_BASE)
ELEMENT_SET.load_files(settings.PATH_ELEMENTS_CUSTOM)
