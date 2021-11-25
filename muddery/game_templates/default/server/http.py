#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

To start the game editor you should run the following command in the game directory.

python server/http.py runserver 0.0.0.0:8000
"""
import os
import sys


def main():
    SETTINGS_DOTPATH = "server.conf.settings"
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_DOTPATH)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
