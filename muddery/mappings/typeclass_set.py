"""
All available requests.
"""

from __future__ import print_function

import os, re, inspect
from importlib import import_module
from pkgutil import iter_modules
from django.conf import settings
from evennia.utils import logger
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
        self.match_class = re.compile(r'^ {4}key\s*=\s*"(.*)"\s*$')

    def load_files(self, typeclass_path):
        """
        Get typeclasses' file path.
        """
        if not typeclass_path:
            return

        module = import_module(typeclass_path)
        base_path = module.__path__
        if base_path:
            base_path = base_path[0]
            for root, dirs, files in os.walk(base_path):
                for filename in files:
                    name, ext = os.path.splitext(filename)
                    if ext != ".py":
                        continue

                    with open(os.path.join(root, filename), "r") as fp:
                        for line in fp.readlines():
                            match = self.match_class.match(line)
                            if match:
                                if base_path == root:
                                    self.module_dict[match.group(1)] = typeclass_path + "." + name
                                else:
                                    relative_path = os.path.relpath(root, base_path)
                                    modlue_path = get_module_path(relative_path)
                                    self.module_dict[match.group(1)] = typeclass_path + "." + modlue_path + "." + name

        print("self.module_dict: %s" % self.module_dict)

    def load_classes(self, typeclass_path):
        """
        Add all typeclasses from the typeclass path.
        """
        for cls in classes_in_path(typeclass_path, BaseTypeclass):
            if not cls.key:
                continue

            if self.class_dict.has_key(cls.key):
                if self.class_dict[cls.key] == cls:
                    continue
                logger.log_infomsg("Typeclass %s is replaced by %s." % (cls.key, cls))

            self.class_dict[cls.key] = cls

    def get(self, key, path=None):
        """
        Get a typeclass recursively.
        """
        if key in self.class_dict:
            return self.class_dict[key]
        elif key in self.module_dict:
            module = import_module(self.module_dict[key])

            # add new typeclasses
            for name, cls in vars(module).items():
                if inspect.isclass(cls) and issubclass(cls, BaseTypeclass):
                    if not cls.key:
                        continue

                    if self.class_dict.has_key(cls.key):
                        if self.class_dict[cls.key] == cls:
                            continue
                        logger.log_infomsg("Typeclass %s is replaced by %s." % (cls.key, cls))

                    self.class_dict[cls.key] = cls

            if key in self.class_dict:
                return self.class_dict[key]

        logger.log_errmsg("Can not find typeclass key: %s." % key)

    def get_group(self, group_key):
        """
        Get a typeclass and its all children.
        """
        cls = self.class_dict[group_key]
        typeclasses = {group_key: cls}

        for key in self.class_dict:
            if issubclass(self.class_dict[key], cls):
                typeclasses[key] = self.class_dict[key]

        return typeclasses


TYPECLASS_SET = TypeclassSet()
TYPECLASS = TYPECLASS_SET.get
TYPECLASS_SET.load_files(settings.PATH_TYPECLASSES_BASE)
TYPECLASS_SET.load_files(settings.PATH_TYPECLASSES_CUSTOM)
TYPECLASS_SET.load_classes(settings.PATH_TYPECLASSES_BASE)
TYPECLASS_SET.load_classes(settings.PATH_TYPECLASSES_CUSTOM)

