"""
Channel

The channel class represents the out-of-character chat-room usable by
Players in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.
"""

from muddery.server.elements.base_element import BaseElement
from muddery.server.server import Server


class MudderyChannel(BaseElement):
    """
    The character not controlled by players.

    States:
        shops
    """
    element_type = "CHANNEL"
    element_name = "Channel"
    model_name = ""

    def at_element_setup(self, first_time):
        """
        Set data_info to the object.
        """
        super(MudderyChannel, self).at_element_setup(first_time)

        # character_list: {
        #   character's db id: character's object
        # }
        self.all_characters = set()

    def add_character(self, char_db_id):
        """
        Add a new character to this channel.
        """
        self.all_characters.add(char_db_id)

    def remove_character(self, char_db_id):
        """
        Remove a character from this channel.
        """
        self.all_characters.remove(char_db_id)

    def get_message(self, caller, message):
        """
        Receive a message from a character.

        :param caller: talker.
        :param message: content.
        """
        for char_db_id in self.all_characters:
            try:
                char = Server.world.get_character(char_db_id)
                char.msg({
                    "conversation": {
                        "type": self.get_element_key(),
                        "channel": self.const.name,
                        "from_id": caller.get_db_id(),
                        "from_name": caller.get_name(),
                        "msg": message,
                    }
                })
            except KeyError:
                self.all_characters.remove(char_db_id)
