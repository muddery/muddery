"""
Muddery text game creation system

This is the main top-level API for Muddery. You can also explore the
muddery library by accessing muddery.<subpackage> directly.

For full functionality you need to explore this module via a django-
aware shell. Go to your game directory and use the command 'muddery.py shell'
to launch such a shell (using python or ipython depending on your install).

See www.muddery.org for full documentation.

"""

from __future__ import print_function

def _create_version():
    """
    Helper function for building the version string
    """
    import os
    from subprocess import check_output, CalledProcessError, STDOUT

    version = "Unknown"
    root = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(root, "VERSION.txt"), 'r') as f:
            version = f.read().strip()
    except IOError as err:
        print(err)
    return version

__version__ = _create_version()
del _create_version


def _init():
    """
    This function is called automatically by the launcher only after
    Muddery has fully initialized all its models. It sets up the API
    in a safe environment where all models are available already.
    """
    pass
