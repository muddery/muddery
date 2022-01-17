"""
Command sets

All commands in the game must be grouped in a cmdset.
"""

from muddery.server.commands.command_set import CommandSet
from muddery.server.commands import combat
from muddery.server.commands import general
from muddery.server.commands import player
from muddery.server.commands import unloggedin


class CharacterCmdSet(CommandSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `goto`, etc available on in-game Character objects. It is merged with
    the `PlayerCmdSet` when a Player puppets a Character.
    """
    @classmethod
    def create(cls):
        """
        Populates the cmdset
        """
        super(CharacterCmdSet, cls).create()
        #
        # any commands you add below will overload the default ones.
        #

        cls.add(general.CmdLook())
        cls.add(general.CmdInventoryObject())
        cls.add(general.CmdEquipmentsObject())
        cls.add(general.CmdLookRoomObj())
        cls.add(general.CmdLookRoomChar())
        cls.add(general.CmdTraverse())
        cls.add(general.CmdInventory())
        cls.add(general.CmdTalk())
        cls.add(general.CmdDialogue())
        cls.add(general.CmdLoot())
        cls.add(general.CmdUse())
        cls.add(general.CmdDiscard())
        cls.add(general.CmdEquip())
        cls.add(general.CmdTakeOff())
        cls.add(general.CmdCastSkill())
        cls.add(general.CmdAttack())
        cls.add(general.CmdUnlockExit())
        cls.add(general.CmdGiveUpQuest())
        cls.add(general.CmdShopping())
        cls.add(general.CmdBuy())
        cls.add(general.CmdSay())
        cls.add(general.CmdQueueUpCombat())
        cls.add(general.CmdQuitCombatQueue())
        cls.add(general.CmdConfirmCombat())
        cls.add(general.CmdRejectCombat())
        cls.add(general.CmdGetRankings())
        cls.add(general.CmdQueryQuest())
        cls.add(general.CmdQuerySkill())

        cls.add(combat.CmdCastCombatSkill())
        cls.add(combat.CmdCombatInfo())
        cls.add(combat.CmdLeaveCombat())

        # Command for test.
        cls.add(general.CmdTest())


class AccountCmdSet(CommandSet):
    """
    This is the cmdset available to the Player at all times. It is
    combined with the `CharacterCmdSet` when the Player puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """
    @classmethod
    def create(cls):
        """
        Populates the cmdset
        """
        super(AccountCmdSet, cls).create()
        #
        # any commands you add below will overload the default ones.
        #
        cls.add(player.CmdQuit())
        cls.add(player.CmdChangePassword())
        cls.add(player.CmdPuppet())
        cls.add(player.CmdPuppetName())
        cls.add(player.CmdUnpuppet())
        cls.add(player.CmdCharCreate())
        cls.add(player.CmdCharDelete())
        cls.add(player.CmdCharAll())
        cls.add(player.CmdDeleteAccount())


class SessionCmdSet(CommandSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """
    @classmethod
    def create(cls):
        """
        Populates the cmdset.
        """
        super(SessionCmdSet, cls).create()

        cls.add(unloggedin.CmdUnloginLook())
        cls.add(unloggedin.CmdCreateAccount())
        cls.add(unloggedin.CmdConnectAccount())
        cls.add(unloggedin.CmdQuitAccount())
