"""
This is adapt from evennia/evennia/players/players.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

Player

The Player represents the game "account" and each login has only one
Player object. A Player is what chats on default channels but has no
other in-game-world existance. Rather the Player puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest players are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the committment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

import json
from evennia.utils.utils import make_iter
from evennia.players.players import DefaultPlayer, DefaultGuest

class MudderyPlayer(DefaultPlayer):
    """
    This class describes the actual OOC player (i.e. the user connecting
    to the MUD). It does NOT have visual appearance in the game world (that
    is handled by the character which is connected to this). Comm channels
    are attended/joined using this object.

    It can be useful e.g. for storing configuration options for your game, but
    should generally not hold any character-related info (that's best handled
    on the character level).

    Can be set using BASE_PLAYER_TYPECLASS.
    """
    def msg(self, text=None, from_obj=None, sessid=None, **kwargs):
        """
        Evennia -> User
        This is the main route for sending data back to the user from the
        server.
        
        Args:
        text (str, optional): data to send
        from_obj (Object or Player, optional): object sending. If given,
        its at_msg_send() hook will be called.
        sessid (int or list, optional): session id or ids to receive this
        send. If given, overrules MULTISESSION_MODE.
        Notes:
        All other keywords are passed on to the protocol.
        """
        raw = kwargs.get("raw", False)
        if not raw:
            try:
                text = json.dumps(text)
            except Exception, e:
                text = json.dumps({"err": "There is an error occurred while outputing messages."})
                logger.log_errmsg("json.dumps failed: %s" % e)

        # set raw=True
        if kwargs:
            kwargs["raw"] = True
        else:
            kwargs = {"raw": True}
        
        if from_obj:
            # call hook
            try:
                from_obj.at_msg_send(text=text, to_obj=self, **kwargs)
            except Exception:
                pass

        # session relay
        if sessid:
            # this could still be an iterable if sessid is an iterable
            sessions = self.get_session(sessid)
            if sessions:
                # this is a special instruction to ignore MULTISESSION_MODE
                # and only relay to this given session.
                kwargs["_nomulti"] = True
                for session in make_iter(sessions):
                    session.msg(text=text, **kwargs)
                return

        # we only send to the first of any connected sessions - the sessionhandler
        # will disperse this to the other sessions based on MULTISESSION_MODE.
        sessions = self.get_all_sessions()
        if sessions:
            sessions[0].msg(text=text, **kwargs)



class MudderyGuest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Players, Guests and their
    characters are deleted after disconnection.
    """
    pass
