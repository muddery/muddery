"""
ServerSession

The serversession is the Server-side in-memory representation of a
user connecting to the game.  Evennia manages one Session per
connection to the game. So a user logged into the game with multiple
clients (if Evennia is configured to allow that) will have multiple
sessions tied to one Player object. All communication between Evennia
and the real-world user goes through the Session(s) associated with that user.

It should be noted that modifying the Session object is not usually
necessary except for the most custom and exotic designs - and even
then it might be enough to just add custom session-level commands to
the SessionCmdSet instead.

This module is not normally called. To tell Evennia to use the class
in this module instead of the default one, add the following to your
settings file:

    SERVER_SESSION_CLASS = "server.conf.serversession.ServerSession"

"""

import json
from evennia.server.serversession import ServerSession as BaseServerSession
from evennia.utils import logger


class ServerSession(BaseServerSession):
    """
    This class represents a player's session and is a template for
    individual protocols to communicate with Evennia.

    Each player gets one or more sessions assigned to them whenever they connect
    to the game server. All communication between game and player goes
    through their session(s).
    """
    def data_out(self, text=None, **kwargs):
        """
        Send Evennia -> User
        Convert to JSON.
        """
        options = None
        if "options" in kwargs:
            options = kwargs.get("options", None)

        if options is None:
            options = {}
            kwargs["options"] = {}

        raw = options.get("raw", False)
        context = kwargs.get("context", "")

        if raw:
            out_text = text
        if self.protocol_key == 'telnet':
            out_text = str(text)
        else:
            # set raw=True
            kwargs["options"].update({"raw": True, "client_raw": True})
            try:
                out_text = json.dumps({"data": text, "context": context}, ensure_ascii=False)
            except Exception as e:
                out_text = json.dumps({"data": {"err": "There is an error occurred while outputing messages."}})
                logger.log_tracemsg("json.dumps failed: %s" % e)

        return super(ServerSession, self).data_out(text=out_text, **kwargs)
