"""
Player Characters

Player Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from django.conf import settings
from evennia.utils.utils import lazy_property
from evennia.utils import logger, search
from muddery.server.elements.base_element import BaseElement
from muddery.server.utils import utils
from muddery.server.utils.builder import build_object
from muddery.server.utils.exception import MudderyError, ERR
from muddery.server.utils.localized_strings_handler import _
from muddery.server.dao.worlddata import WorldData
from muddery.server.mappings.element_set import ELEMENT
from muddery.server.utils import defines


class MudderyInventory(BaseElement):
    """
    The character's inventory.
    """
    element_key = "INVENTORY"
    element_name = _("Inventory", "elements")

    def __init__(self, owner):
        """
        Load the inventory and set its owner.
        :param owner: (object) the owner's object
        """
        self.owner_key = owner.get_data_key()
        self.owner_dbref = owner.dbref
        self.id = owner.get_id()

    def get_id(self):
        """
        Get the object's id.

        :return: (number) object's id
        """
        return self.id

    def load_default_objects(self, object_list):
        """
        Load character's default objects.
        """
        contents = self.state.load("contents")
        append_list = []
        for obj in object_list:
            found = False
            for item in contents:
                if obj.object == item["key"]:
                    found = True
                    break

            if not found:
                append_list.append({
                    "object": obj.object,
                    "level": obj.level,
                    "number": obj.number,
                })

        if append_list:
            self.add_objects(append_list)

    def add_objects(self, obj_list):
        """
        Add objects to the inventory.

        Args:
            obj_list: (list) a list of object keys and there numbers.
                             list item: {"object": object's key
                                         "number": object's number}
            mute: (boolean) do not send messages to the owner

        Returns:
            (list) a list of objects that not have been received and their reasons.
            [{
                "key": key,
                "name": name,
                "level": level,
                "number": number,
                "icon": icon,
                "reject": reason,
            }]
        """
        objects = []           # objects that have been accepted

        # check what the character has now
        current_contents = {}
        changed = False
        new_contents = self.state.load("contents", [])
        for item in new_contents:
            key = item["key"]
            if key in current_contents:
                # if the character has more than one item of the same kind,
                # get the smallest stack.
                if current_contents[key]["number"] > item["number"]:
                    current_contents[key] = item
            else:
                current_contents[key] = item

        for obj in obj_list:
            key = obj["object"]
            level = obj.get("level")
            available = obj["number"]
            name = ""
            icon = ""
            number = available
            accepted = 0
            reject = False

            object_record = None
            try:
                common_model_name = ELEMENT("COMMON_OBJECT").model_name
                object_record = WorldData.get_table_data(common_model_name, key=key)
                object_record = object_record[0]
            except Exception as e:
                pass

            if not object_record:
                # can not find object's data record
                continue

            if number == 0:
                # it is an empty object
                if key in current_contents:
                    # already has this object
                    continue

                if object_record.can_remove:
                    # remove this empty object
                    continue

                # create a new content
                new_obj = build_object(key, level=level)
                if new_obj:
                    # move the new object to the inventory
                    new_contents.append({
                        "key": key,
                        "dbref": new_obj.dbref,
                        "obj": new_obj,
                        "number": number,
                    })
                    changed = True
                else:
                    reject = _("Can not get %s.") % key

            else:
                # common number
                # if already has this kind of object
                if key in current_contents:
                    add = number
                    if add > object_record.max_stack - current_contents[key]["number"]:
                        add = object_record.max_stack - current_contents[key]["number"]

                    if add > 0:
                        # increase stack number
                        current_contents[key]["number"] += add
                        number -= add
                        accepted += add

                # if does not have this kind of object, or stack is full
                while number > 0:
                    if object_record.unique:
                        # can not have more than one unique objects
                        reject = _("Can not get more %s.") % name
                        break

                    # create a new content
                    new_obj = build_object(key, level=level)
                    if not new_obj:
                        reject = _("Can not get %s.") % name
                        break

                    # Get the number that actually added.
                    add = number
                    if add > object_record.max_stack:
                        add = object_record.max_stack

                    # move the new object to the inventory
                    new_contents.append({
                        "key": key,
                        "dbref": new_obj.dbref,
                        "obj": new_obj,
                        "number": add,
                    })
                    changed = True

                    number -= add
                    accepted += add

            objects.append({
                "key": object_record.key,
                "name": object_record.name,
                "icon": object_record.icon,
                "number": accepted,
                "reject": reject,
            })

        if changed:
            self.state.save("inventory", new_contents)

        return objects

    def get_object_number(self, obj_key):
        """
        Get the number of this object.
        Args:
            obj_key: (String) object's key

        Returns:
            int: object number
        """
        contents = self.state.load("contents")

        # get total number
        return sum([item["number"] for item in contents if item["key"] == obj_key])

    def can_get_object(self, obj_key, number):
        """
        Check if the character can get these objects.

        Args:
            obj_key: (String) object's key
            number: (int) object's number

        Returns:
            boolean: can get

        Notice:
            If the character does not have this object, the return will be always true,
            despite of the number!
        """
        object_record = None
        try:
            common_model_name = ELEMENT("COMMON_OBJECT").model_name
            object_record = WorldData.get_table_data(common_model_name, key=obj_key)
            object_record = object_record[0]
        except Exception as e:
            return False

        if not object_record.unique:
            return True

        contents = self.state.load("contents")
        if not contents:
            return True

        for item in contents:
            if item["key"] == obj_key:
                return item["number"] + number <= object_record.max_stack

        return True

    def remove_object(self, obj_key):
        """
        Remove an object.

        Args:
            obj_key: (string) object' key
        """
        self.remove_objects({
            "object": obj_key,
            "number": 1,
        })

    def remove_objects(self, obj_list):
        """
        Remove objects from the inventory.

        Args:
            obj_list: (list) a list of object keys and there numbers.
                             list item: {"object": object's key
                                         "number": object's number}

        Returns:
            boolean: success
        """
        contents = self.state.load("contents")
        for obj in obj_list:
            # get total number
            total = sum([item["number"] for item in contents if item["key"] == obj["object"]])
            if total < obj["number"]:
                raise MudderyError(ERR.invalid_input, "Not enough number %s." % obj["object"])

            # remove objects
            to_remove = total
            try:
                i = 0
                while i < len(contents):
                    item = contents[i]
                    if item["key"] != obj["object"]:
                        i += 1
                        continue

                    deleted = False
                    if item["number"] > 0:
                        if item["number"] >= to_remove:
                            to_remove = 0
                            item["number"] -= to_remove
                        else:
                            to_remove -= item["number"]
                            item["number"] = 0

                        if obj.get_number() <= 0:
                            # If this object can be removed from the inventor.
                            if obj.can_remove:
                                # if it is an equipment, take off it first
                                inventory[i].delete()
                                del inventory[i]
                                deleted = True

                    if to_remove <= 0:
                        break

                    if not deleted:
                        i += 1

            except Exception as e:
                logger.log_tracemsg("Can not remove object %s: %s" % (obj["object"], e))
                return False

            if to_remove > 0:
                logger.log_err("Remove object error: %s" % obj["object"])
                return False

        return True

    def show_inventory(self):
        """
        Send inventory data to player.
        """
        self.msg({"inventory": self.return_inventory()})

    def return_inventory(self):
        """
        Get inventory's data.
        """
        inv = []
        inventory = self.state.load("inventory", [])
        for item in inventory:
            info = {"dbref": item.dbref,        # item's dbref
                    "name": item.name,          # item's name
                    "number": item.get_number(),   # item's number
                    "desc": item.db.desc,       # item's desc
                    "can_remove": item.can_remove,
                    "icon": getattr(item, "icon", None)}  # item's icon
            
            if getattr(item, "equipped", False):
                info["equipped"] = item.equipped
            inv.append(info)

        # sort by created time
        inv.sort(key=lambda x:x["dbref"])

        return inv
