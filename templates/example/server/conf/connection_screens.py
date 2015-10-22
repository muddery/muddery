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
    Welcome to the demo game of Muddery! This version is created on Oct. 23, 2015.
    
    This demo game is based on Muddery, an open-source online text game server. If you are interested in it, please visit our website www.muddery.org.
    
    {rNotice! This game is for demo only, all players' register info and game data may be lost frequently!{n
{b=============================================================={n"""

# % (settings.SERVERNAME, utils.get_muddery_version())
