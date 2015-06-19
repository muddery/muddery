"""
ObjectSpawner is the helper class that creates objects.

"""

from muddery.utils.builder import build_object
from muddery.utils.object_key_handler import OBJECT_KEY_HANDLER
from evennia.utils import logger


def create_object(character, object_list):
    """
    Create objects.
    args:
        character: (object) the character who will get objects.
        object_list: (dict) a list of object keys, in the form of:
            {object_key1:number,
             object_key2:number,
             ...
            }
    """
    if not character:
        return

    accepted_keys = {}
    accepted_names = {}
    rejected_keys = {}
    rejected_names = {}

    for key in object_list:
        # parse the arg
        model = OBJECT_KEY_HANDLER.get_model(key)
        if not model:
            logger.log_errmsg("Unknown object key: %s" % key)
            continue
        
        # find object's info
        new_obj = build_object(model, key)
                    
        #move the object to the character
        if not new_obj.move_to(character, quiet=True, emit_to_obj=character):
            new_obj.delete()
            rejected_keys[key] = object_list[key]
            rejected_names[new_obj.name] = object_list[key]
        else:
            accepted_keys[key] = object_list[key]
            accepted_names[new_obj.name] = object_list[key]

    message = {"get_object":
                    {"accepted": accepted_names,
                     "rejected": rejected_names}}
    character.msg(message)
    character.show_inventory()
