"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

import os, inspect
import asyncio
import importlib
from pkgutil import iter_modules


def get_muddery_version():
    """
    Get muddery's version.
    """
    import muddery
    return muddery.__version__


def file_iterator(file, erase=False, chunk_size=512):
    while True:
        c = file.read(chunk_size)
        if c:
            yield c
        else:
            # remove temp file
            file.close()
            if erase:
                os.remove(file.name)
            break


def class_from_path(path):
    """
    Get a class from its path
    :param path:
    :return:
    """
    class_path, class_name = path.rsplit(".", 1)

    mod = importlib.import_module(class_path)
    cls = getattr(mod, class_name)
    return cls


def load_modules(path):
    """
    Load all modules ans sub modules in the path.

    Args:
        path: (string) modules' path
    """
    modules = []
    m = importlib.import_module(path)
    if hasattr(m, '__path__'):
        for _, subpath, ispkg in iter_modules(m.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                modules += load_modules(fullpath)
            else:
                modules.append(importlib.import_module(fullpath))

    return modules


def classes_in_path(path, cls):
    """
    Load all classes in the path.

    Args:
        path: (string) classes' path
        cls: (class) classes' base class
    """
    modules = load_modules(path)
    for module in modules:
        items = [obj for obj in vars(module).values() if inspect.isclass(obj) and issubclass(obj, cls) and obj is not cls]
        for obj in items:
            yield obj


def get_module_path(path):
    """
    Transform a normal path to a python module style path.
    """
    root, name = os.path.split(path)
    if not name:
        return

    root = get_module_path(root)
    if root:
        return root + "." + name
    else:
        return name


async def async_wait(coros: list):
    """
    Wrap the system asyncio.wait function.
    """
    return await asyncio.wait([asyncio.create_task(c) for c in coros])


async def async_gather(coros: list):
    """
    Wrap the system asyncio.gather function.
    """
    return await asyncio.gather(*coros)


def write_pid_file(filename, pid):
    """
    Write a pid to a file.
    """
    with open(filename, "w") as fp:
        fp.write(str(pid))


def read_pid_file(filename):
    """
    Read a pid from a file.
    """
    pid = None
    try:
        with open(filename, "r") as fp:
            pid = fp.readline()
            pid = int(pid)
    except FileNotFoundError:
        pass

    return pid
