"""
Channel

The channel class represents the out-of-character chat-room usable by
Players in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.

Note that sending data to channels are handled via the CMD_CHANNEL
syscommand (see evennia.syscmds). The sending should normally not need
to be modified.

"""

import json
from evennia.comms.models import TempMsg
from evennia.comms.comms import DefaultChannel
from evennia.utils.utils import make_iter
from muddery.utils.localized_strings_handler import _
from muddery.utils.defines import ConversationType


class MudderyChannel(DefaultChannel):
    """
    Working methods:
        at_channel_creation() - called once, when the channel is created
        has_connection(player) - check if the given player listens to this channel
        connect(player) - connect player to this channel
        disconnect(player) - disconnect player from channel
        access(access_obj, access_type='listen', default=False) - check the
                    access on this channel (default access_type is listen)
        delete() - delete this channel
        message_transform(msg, emit=False, prefix=True,
                          sender_strings=None, external=False) - called by
                          the comm system and triggers the hooks below
        msg(msgobj, header=None, senders=None, sender_strings=None,
            persistent=None, online=False, emit=False, external=False) - main
                send method, builds and sends a new message to channel.
        tempmsg(msg, header=None, senders=None) - wrapper for sending non-persistent
                messages.
        distribute_message(msg, online=False) - send a message to all
                connected players on channel, optionally sending only
                to players that are currently online (optimized for very large sends)

    Useful hooks:
        channel_prefix(msg, emit=False) - how the channel should be
                  prefixed when returning to user. Returns a string
        format_senders(senders) - should return how to display multiple
                senders to a channel
        pose_transform(msg, sender_string) - should detect if the
                sender is posing, and if so, modify the string
        format_external(msg, senders, emit=False) - format messages sent
                from outside the game, like from IRC
        format_message(msg, emit=False) - format the message body before
                displaying it to the user. 'emit' generally means that the
                message should not be displayed with the sender's name.

        pre_join_channel(joiner) - if returning False, abort join
        post_join_channel(joiner) - called right after successful join
        pre_leave_channel(leaver) - if returning False, abort leave
        post_leave_channel(leaver) - called right after successful leave
        pre_send_message(msg) - runs just before a message is sent to channel
        post_send_message(msg) - called just after message was sent to channel

    """

    def channel_prefix(self, msg=None, emit=False, **kwargs):

        """
        Hook method. How the channel should prefix itself for users.

        Args:
            msg (str, optional): Prefix text
            emit (bool, optional): Switches to emit mode, which usually
                means to not prefix the channel's info.

        Returns:
            prefix (str): The created channel prefix.
        """
        return '' if emit else '[%s] ' % _(self.key, category="channels")

    def get_message(self, caller, message):
        """
        Receive a message from a character.

        :param caller: talker.
        :param message: content.
        """
        if not self.access(caller, "send"):
            caller.msg(_("You can not talk in this channel."))
            return

        output = {
            "conversation": {
                "type": ConversationType.CHANNEL.value,
                "channel": _(self.key, category="channels"),
                "from_dbref": caller.dbref,
                "from_name": caller.get_name(),
                "msg": message,
            }
        }
        msgobj = TempMsg(message=output, channels=[self])
        self.msg(msgobj, emit=True)

    def msg(
        self,
        msgobj,
        header=None,
        senders=None,
        sender_strings=None,
        keep_log=None,
        online=False,
        emit=False,
        external=False,
    ):
        """
        Send the given message to all accounts connected to channel. Note that
        no permission-checking is done here; it is assumed to have been
        done before calling this method. The optional keywords are not used if
        persistent is False.

        Args:
            msgobj (Msg, TempMsg or str): If a Msg/TempMsg, the remaining
                keywords will be ignored (since the Msg/TempMsg object already
                has all the data). If a string, this will either be sent as-is
                (if persistent=False) or it will be used together with `header`
                and `senders` keywords to create a Msg instance on the fly.
            header (str, optional): A header for building the message.
            senders (Object, Account or list, optional): Optional if persistent=False, used
                to build senders for the message.
            sender_strings (list, optional): Name strings of senders. Used for external
                connections where the sender is not an account or object.
                When this is defined, external will be assumed.
            keep_log (bool or None, optional): This allows to temporarily change the logging status of
                this channel message. If `None`, the Channel's `keep_log` Attribute will
                be used. If `True` or `False`, that logging status will be used for this
                message only (note that for unlogged channels, a `True` value here will
                create a new log file only for this message).
            online (bool, optional) - If this is set true, only messages people who are
                online. Otherwise, messages all accounts connected. This can
                make things faster, but may not trigger listeners on accounts
                that are offline.
            emit (bool, optional) - Signals to the message formatter that this message is
                not to be directly associated with a name.
            external (bool, optional): Treat this message as being
                agnostic of its sender.

        Returns:
            success (bool): Returns `True` if message sending was
                successful, `False` otherwise.

        """
        senders = make_iter(senders) if senders else []
        if isinstance(msgobj, str):
            # given msgobj is a string - convert to msgobject (always TempMsg)
            msgobj = TempMsg(senders=senders, header=header, message=msgobj, channels=[self])
        # we store the logging setting for use in distribute_message()
        msgobj.keep_log = keep_log if keep_log is not None else self.db.keep_log

        # start the sending
        msgobj = self.pre_send_message(msgobj)
        if not msgobj:
            return False
        msgobj = self.message_transform(
            msgobj, emit=emit, prefix=False, sender_strings=sender_strings, external=external
        )
        self.distribute_message(msgobj, online=online)
        self.post_send_message(msgobj)
        return True
