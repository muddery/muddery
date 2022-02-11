"""
Muddery online game creation system
See www.muddery.org for full documentation.
"""
import traceback


def _create_version():
    """
    Helper function for building the version string
    """
    import os
    from subprocess import check_output, CalledProcessError, STDOUT

    version = "Unknown"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(root, "VERSION.txt"), 'r') as f:
            version = f.read().strip()
    except IOError as err:
        traceback.print_exc()
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
