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
  欢迎来到开源软件 Muddery 的演示游戏！当前版本的日期为{y2015年7月29日{n。

  这是一款很小的适合单人游玩的游戏，游戏情节很短，仅用于展示 Muddery 系统的特性。由于会不定期地更改游戏代码及数据库结构，{r用户的游戏进度、数据可能会部分或全部丢失{n，敬请谅解。
 
  Muddery 是一个用Python编写的在线文字游戏框架，采用BSD许可协议发布，它基于Evennia（一个创建MUD类游戏的系统）开发，如果您对它感兴趣，欢迎访问我们的网站 {whttp://www.evenniacn.com{n 以获取更多信息 。
{b=============================================================={n"""

# % (settings.SERVERNAME, utils.get_muddery_version())
