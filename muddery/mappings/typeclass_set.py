"""
All available requests.
"""

from __future__ import print_function

import os, re, inspect
from importlib import import_module
from pkgutil import iter_modules
from django.conf import settings
from evennia.utils import logger
from evennia.utils.utils import class_from_module
from muddery.utils.exception import MudderyError
from muddery.utils.utils import classes_in_path, load_modules, get_module_path
from muddery.typeclasses.base_typeclass import BaseTypeclass


class TypeclassSet(object):
    """
    All available typeclasses.
    """
    def __init__(self):
        self.module_dict = {}
        self.class_dict = {}
        self.trigger_dict = {}

        self.all_loaded = False
        self.match_class = re.compile(r'^class\s+(\w+)\s*.*$')
        self.match_key = re.compile(r""" {4}typeclass_key\s*=\s*("|')(.+)("|')\s*$""")

    def load_files(self, typeclass_path):
        """
        Get typeclasses' file path.
        """
        if not typeclass_path:
            return

        module = import_module(typeclass_path)
        base_path = module.__path__
        if not base_path:
            return

        base_path = base_path[0]
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext != ".py":
                    continue

                with open(os.path.join(root, filename), "r") as fp:
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

                                module_path = typeclass_path
                                if base_path == root:
                                    module_path += "." + name + "." + class_name
                                else:
                                    relative_path = get_module_path(os.path.relpath(root, base_path))
                                    module_path += "." + relative_path + "." + name + "." + class_name

                                if key_name in self.module_dict:
                                    logger.log_infomsg("Typeclass %s is replaced by %s." % (key_name, module_path))

                                self.module_dict[key_name] = module_path
                                class_name = ""

    def load_classes(self):
        """
        Add all typeclasses from the typeclass path.

        To prevent loop import, call this method later.
        """
        if self.all_loaded:
            return

        for key in self.module_dict:
            if self.class_dict.has_key(key):
                continue
            cls = class_from_module(self.module_dict[key])
            self.class_dict[key] = cls
            self.trigger_dict[key] = cls.get_event_trigger_types()

        self.all_loaded = True

    def get(self, key):
        """
        Get a typeclass recursively.
        """
        if key in self.class_dict:
            return self.class_dict[key]
        elif key in self.module_dict:
            cls = class_from_module(self.module_dict[key])
            if self.class_dict.has_key(key):
                if self.class_dict[key] != cls:
                    logger.log_infomsg("Typeclass %s is replaced by %s." % (key, cls))

            self.class_dict[key] = cls
            self.trigger_dict[key] = cls.get_event_trigger_types()
            return cls

        logger.log_errmsg("Can not find typeclass key: %s." % key)

    def get_module(self, key):
        """
        Get a typeclass's module path.
        """
        return self.module_dict.get(key, None)

    def get_group(self, group_key):
        """
        Get a typeclass and its all children.
        """
        self.load_classes()

        cls = self.class_dict[group_key]
        typeclasses = {group_key: cls}

        for key in self.class_dict:
            if issubclass(self.class_dict[key], cls):
                typeclasses[key] = self.class_dict[key]

        return typeclasses

    def get_trigger_types(self, key):
        """
        Get a typeclass's trigger types.
        """
        self.load_classes()

        return self.trigger_dict.get(key, [])

    def get_all_info(self):
        """
        Get all typeclass's information.

        Return: (dict) all typeclass's information.
        """
        self.load_classes()

        info = {}
        for key, cls in self.class_dict.items():
            # Get the class's parent which has another typeclass name.
            bases = cls.__bases__
            parent_key = ""
            while not parent_key:
                has_typeclass_key = False
                for base in bases:
                    if hasattr(base, "typeclass_key") and base.typeclass_key:
                        has_typeclass_key = True

                        if base.typeclass_key != cls.typeclass_key:
                            parent_key = base.typeclass_key
                        else:
                            bases = base.__bases__
                        break

                if not has_typeclass_key:
                    break

            info[key] = {
                "name": cls.typeclass_name,
                "parent": parent_key
            }

        return info


TYPECLASS_SET = TypeclassSet()
TYPECLASS = TYPECLASS_SET.get
TYPECLASS_SET.load_files(settings.PATH_TYPECLASSES_BASE)
TYPECLASS_SET.load_files(settings.PATH_TYPECLASSES_CUSTOM)
