"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

import traceback
from evennia import CmdSet
from evennia import default_cmds
from muddery.commands import combat
from muddery.commands import general
from muddery.commands import player
from muddery.commands import unloggedin
from muddery.commands import worlddata

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `PlayerCmdSet` when a Player puppets a Character.
    """
    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(CharacterCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(worlddata.CmdImportData())
        self.add(worlddata.CmdSetDataInfo())
        self.add(worlddata.CmdLoadWorld())

        self.add(general.CmdLook())
        self.add(general.CmdGoto())
        self.add(general.CmdInventory())
        self.add(general.CmdTalk())
        self.add(general.CmdDialogue())
        self.add(general.CmdLoot())
        self.add(general.CmdUse())
        self.add(general.CmdDiscard())
        self.add(general.CmdEquip())
        self.add(general.CmdTakeOff())
        self.add(general.CmdCastSkill())
        self.add(general.CmdAttack())
        self.add(general.CmdUnlockExit())
        self.add(general.CmdGiveUpQuest())
        
        # Add empty login cmd and skill cmd to the normal cmdset to
        # avoid wrong cmd messages.
        self.add(general.CmdConnect())
        self.add(general.CmdCreate())
        self.add(general.CmdCreateConnect())


class PlayerCmdSet(default_cmds.PlayerCmdSet):
    """
    This is the cmdset available to the Player at all times. It is
    combined with the `CharacterCmdSet` when the Player puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """
    key = "DefaultPlayer"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(PlayerCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(player.CmdQuit())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """
    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        # super(UnloggedinCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(unloggedin.CmdUnconnectedLoginStart())
        self.add(unloggedin.CmdUnconnectedLook())
        self.add(unloggedin.CmdUnconnectedCreateConnect())
        self.add(unloggedin.CmdUnconnectedConnect())
        self.add(unloggedin.CmdUnconnectedQuit())


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """
    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super(SessionCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class CombatCmdSet(CmdSet):
    """
    When players are in combat, the combat cmdset will replace the normal cmdset.
    The normal cmdset will be recoverd when the combat is over.
    """
    key = "combat_cmdset"
    mergetype = "Replace"
    priority = 10 
    no_exits = True

    def at_cmdset_creation(self):
        self.add(general.CmdLook())
        self.add(general.CmdCastSkill())
        self.add(combat.CmdCombatInfo())
