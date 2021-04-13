"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

"""

from evennia import CmdSet
from evennia import default_cmds
from muddery.server.commands import combat
from muddery.server.commands import general
from muddery.server.commands import player
from muddery.server.commands import unloggedin


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `goto`, etc available on in-game Character objects. It is merged with
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

        self.add(general.CmdLook())
        self.add(general.CmdInventoryObject())
        self.add(general.CmdEquipmentsObject())
        self.add(general.CmdLookRoomObj())
        self.add(general.CmdTraverse())
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
        self.add(general.CmdShopping())
        self.add(general.CmdBuy())
        self.add(general.CmdSay())
        self.add(general.CmdQueueUpCombat())
        self.add(general.CmdQuitCombatQueue())
        self.add(general.CmdConfirmCombat())
        self.add(general.CmdRejectCombat())
        self.add(general.CmdGetRankings())
        self.add(general.CmdQueryQuest())
        self.add(general.CmdQuerySkill())

        self.add(combat.CmdCastCombatSkill())
        self.add(combat.CmdCombatInfo())
        self.add(combat.CmdLeaveCombat())

        # Add empty login commands to the normal cmdset to
        # avoid showing wrong cmd messages.
        self.add(general.CmdConnect())
        self.add(general.CmdCreate())
        self.add(general.CmdCreateConnect())

        # Command for test.
        self.add(general.CmdTest())

class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Player at all times. It is
    combined with the `CharacterCmdSet` when the Player puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """
    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(AccountCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(player.CmdQuit())
        self.add(player.CmdChangePassword())
        self.add(player.CmdPuppet())
        self.add(player.CmdUnpuppet())
        self.add(player.CmdCharCreate())
        self.add(player.CmdCharDelete())
        self.add(player.CmdCharAll())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """
    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset.
        """
        self.add(unloggedin.CmdUnconnectedLoginStart())
        self.add(unloggedin.CmdUnconnectedCreate())
        self.add(unloggedin.CmdUnconnectedConnect())
        self.add(unloggedin.CmdUnconnectedQuit())
        self.add(unloggedin.CmdQuickLogin())
        self.add(unloggedin.CmdUnconnectedConnectT())


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
