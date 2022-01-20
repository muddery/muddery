"""
General helper functions that don't fit neatly under any given category.

They provide some useful string and conversion methods that might
be of use when designing your own game.

"""

import os, re, inspect
import importlib
from pkgutil import iter_modules
from muddery.server.settings import SETTINGS
from muddery.launcher import configs
from muddery.server.database.worlddata.localized_strings import LocalizedStrings


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


def get_unlocalized_py_strings(filename, filter):
    """
    Get all unlocalized strings.

    Args:
        file_type: (string) type of file.
        filter: (boolean) filter exits strings or not.
        
    Returns:
        (set): a list of tuple (string, category).
    """
    re_func = re.compile(r'_\(\s*".+?\)')
    re_string = re.compile(r'".*?"')
    re_category = re.compile(r'category.*=.*".*?"')
    strings = set()
    
    # search in python files
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            # parse _() function
            for func in re_func.findall(line):
                str = ""
                cate = ""
                
                str_search = re_string.search(func)
                if str_search:
                    str = str_search.group()
                    #remove quotations
                    str = str[1:-1]
                    
                    cate_search = re_category.search(func)
                    if cate_search:
                        group = cate_search.group()
                        cate = re_string.search(group).group()
                        #remove quotations
                        cate = cate[1:-1] 

                if str or cate:
                    if filter:
                        # check database
                        try:
                            LocalizedStrings.get(str, cate)
                            continue
                        except Exception as e:
                            pass

                    strings.add((str, cate,))

    return strings


def all_unlocalized_py_strings(filter):
    """
    Get all unlocalized strings.
    
    Args:
        file_type: (string) type of file.
        filter: (boolean) filter exits strings or not.

    Returns:
        (set): a list of tuple (string, category).
    """
    rootdir = configs.MUDDERY_LIB
    strings = set()
    ext = ".py"
    
    # get all _() args in all files
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == ext:
                full_name = os.path.join(parent, filename)
                strings.update(get_unlocalized_py_strings(full_name, filter))
    return strings


def get_unlocalized_js_strings(filename, filter_set):
    """
    Get all unlocalized strings.

    Args:
        file_type: (string) type of file.
        filter_set: (set) current localized stings set.
        
    Returns:
        (set): a list of strings.
    """
    re_func = re.compile(r'_\(\s*".+?\)')
    re_string = re.compile(r'".*?"')
    strings = set()
    
    # search in python files
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            # parse _() function
            for func in re_func.findall(line):
                str = ""
                cate = ""
                
                str_search = re_string.search(func)
                if str_search:
                    str = str_search.group()
                    #remove quotations
                    str = str[1:-1]

                if str:
                    if filter_set:
                        # check dict
                        if str not in filter_set:
                            strings.add(str)
                    else:
                        strings.add(str)
    return strings


def all_unlocalized_js_strings(filter):
    """
    Get all unlocalized strings.
    
    Args:
        file_type: (string) type of file.
        filter: (boolean) filter exits strings or not.

    Returns:
        (set): a list of tuple (string, category).
    """
    rootdir = configs.MUDDERY_LIB
    strings = set()
    ext = ".js"
    
    filter_set = set()
    # get filter
    if filter:
        local_string_filename = os.path.join(configs.MUDDERY_LIB, "web", "webclient", "webclient",
                                             "lang", SETTINGS.LANGUAGE_CODE, "strings.js")
        with open(local_string_filename, "r") as file:
            re_dict = re.compile(r'".+?"\s*:\s*".+?"')
            re_string = re.compile(r'".*?"')

            lines = file.readlines()
            for line in lines:
                # find localization dict
                dict_search = re_dict.search(line)
                if dict_search:
                    word_dict = dict_search.group()
                    str_search = re_string.search(word_dict)
                    str = str_search.group()

                    #remove quotations
                    str = str[1:-1]
                    filter_set.add(str)
    
    # get all _() args in all files
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == ext:
                full_name = os.path.join(parent, filename)
                strings.update(get_unlocalized_js_strings(full_name, filter_set))
    return strings


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
