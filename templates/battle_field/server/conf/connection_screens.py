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
  欢迎来到开源软件 Muddery 的演示游戏！当前版本的日期为{y2015年10月14日{n。

  这是一款很小的单人游戏，游戏情节很短，仅用于展示 Muddery 系统的特性。由于会不定期地更改游戏代码及数据库结构，{r用户的游戏信息可能会丢失，如果原用户名无法登陆，请重新注册{n，敬请谅解。
 
  Muddery 是一个用Python编写的开源的在线文字游戏框架，更多信息欢迎访问网站 {whttp://cn.muddery.org{n 。
{b=============================================================={n"""

# % (settings.SERVERNAME, utils.get_muddery_version())
