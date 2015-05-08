"""
This is adapt from evennia/evennia/objects/objects.py.
The licence of Evennia can be found in evennia/LICENSE.txt.

MudderyObject is an object which can load it's data automatically.

"""

import json
from evennia.objects.objects import DefaultObject
from muddery.utils import loader


class MudderyObject(DefaultObject):
    """
    This object loads attributes from world data on init automatically.
    """

    def at_init(self):
        """
        Load world data.
        """
        super(MudderyObject, self).at_init()

        # need save before modify m2m fields
        self.save()

        try:
            loader.load_data(self)
        except Exception, e:
            logger.log_errmsg("%s can not load data:%s" % (this.dbref, e))


    def get_surroundings(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """

        # get name, description, commands and all objects in it
        info = {"dbref": self.dbref,
                "name": self.name,
                "desc": self.db.desc,
                "commands": self.get_available_commands(caller),
                "exits": [],
                "players": [],
                "things": []}

        visible = (cont for cont in self.contents if cont != caller and
                   cont.access(caller, "view"))

        for cont in visible:
            if cont.destination:
                info["exits"].append({"dbref":cont.dbref,
                                     "name":cont.name})
            elif cont.player:
                info["players"].append({"dbref":cont.dbref,
                                       "name":cont.name})
            else:
                info["things"].append({"dbref":cont.dbref,
                                      "name":cont.name})

        return info


    def get_appearance(self, caller):
        """
        This is a convenient hook for a 'look'
        command to call.
        """
            
        # get name and description
        info = {"dbref": self.dbref,
                "name": self.name,
                "desc": self.db.desc,
                "commands": self.get_available_commands(caller)}
                
        return info
            
            
    def get_available_commands(self, caller):
        """
        This returns a list of available commands.
        """
        commands = [{"name":"LOOK", "cmd":"look", "args":self.dbref}]
        return commands


    def msg(self, text=None, from_obj=None, sessid=0, **kwargs):
        """
        Emits something to a session attached to the object.
        
        Args:
        text (str, optional): The message to send
        from_obj (obj, optional): object that is sending. If
        given, at_msg_send will be called
        sessid (int or list, optional): sessid or list of
        sessids to relay to, if any. If set, will
        force send regardless of MULTISESSION_MODE.
        Notes:
        `at_msg_receive` will be called on this Object.
        All extra kwargs will be passed on to the protocol.
        
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
                log_trace()
        try:
            if not self.at_msg_receive(text=text, **kwargs):
                # if at_msg_receive returns false, we abort message to this object
                return
        except Exception:
            log_trace()
                                                        
        # session relay
        kwargs['_nomulti'] = kwargs.get('_nomulti', True)

        if self.player:
            # for there to be a session there must be a Player.
            if sessid:
                sessions = make_iter(self.player.get_session(sessid))
            else:
                # Send to all sessions connected to this object
                sessions = [self.player.get_session(sessid) for sessid in self.sessid.get()]
            if sessions:
                sessions[0].msg(text=text, session=sessions, **kwargs)
