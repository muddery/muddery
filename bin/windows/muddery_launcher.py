#! /usr/bin/python
"""
Windows launcher. This is called by a dynamically created .bat file in
the python bin directory and makes the 'muddery' program available on
the command %path%.
"""

import os, sys

# for pip install -e
sys.path.insert(0, os.path.abspath(os.getcwd()))
# main library path
sys.path.insert(0, os.path.join(sys.prefix, "Lib", "site-packages"))

from  muddery.server import muddery_launcher
muddery_launcher.main()
