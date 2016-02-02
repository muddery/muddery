# -*- coding: utf-8 -*-
"""
Connection screen

Texts in this module will be shown to the user at login-time.

Muddery will look at global string variables (variables defined
at the "outermost" scope of this module and use it as the
connection screen. If there are more than one, Muddery will
randomize which one it displays.

The commands available to the user when the connection screen is shown
are defined in commands.default_cmdsets.UnloggedinCmdSet and the
screen is read and displayed by the unlogged-in "look" command.

"""

from django.conf import settings
from muddery.utils import utils

CONNECTION_SCREEN = \
"""{b=============================================================={n
  Welcome to Muddery's demo game! This version is created on {yFeb. 1, 2016{n.

  This is a small solo game. It's very short, only to demonstrate Muddery's abilities.
  Because the game codes and the database structure may change frequently, user's data may lose. {rIf you can not login with your username, please register again.{n
 
  Muddery is an open source online text game framework in Python. For more information, please visit our website {whttp://www.muddery.org{n.
{b=============================================================={n"""

# % (settings.SERVERNAME, utils.get_muddery_version())
