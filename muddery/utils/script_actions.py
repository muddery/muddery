"""
Default action scripts are in this model.
Action script functions must be compatible with this:

def func(character, obj, *args)
    args:
        character(object): a player character.
        obj(object): the player character's action target.
        args: other args.

"""

from muddery.utils import utils


def example(caller, obj, *args):
    """
    This is an example.
    """
    return


def learn_skill(character, obj, *args):
    """
    Teach the character a skill.
    args: skill's key
    """
    if not character:
        return

    if not args:
        return

    character.skill_handler.learn_skill(args[0])


def give_objects(character, obj, *args):
    """
    Give some objects to the character.
    args: object's key and object's number
    """
    if not character:
        return

    if not args:
        return

    obj_key = args[0]
    number = 1
    if len(args) > 1:
        number = args[1]

    obj_list = [{"object": obj_key,
                 "number": number}]

    character.receive_objects(obj_list)


def remove_objects(character, obj, *args):
    """
    Remove some objects from the character.
    args:
        args[0]: object's key
        args[1]: object's number
    """
    if not character:
        return

    if not args:
        return

    obj_key = args[0]
    number = 1
    if len(args) > 1:
        number = args[1]

    obj_list = [{"object": obj_key,
                 "number": number}]

    character.remove_objects(obj_list)


def teleport_to(character, obj, *args):
    """
    Teleport the character to specified room.
    args: target room's key
    """
    if not character:
        return

    if not args:
        return

    destination = utils.search_obj_data_key(args[0])
    if not destination:
        return
    destination = destination[0]

    character.move_to(destination)


def set_attr(character, obj, *args):
    """
    Set the character's attribute.
    args:
        args[0]: attribute key
        args[1](optional): attribute value
    """
    if not character:
        return

    if not args:
        return

    key = args[0]
    value = None
    if len(args) > 1:
        value = args[1]

    character.custom_attr.set(key, value)


def get_attr(character, obj, *args):
    """
    Get the character's attribute.
        args:
        args[0]: attribute key
        args[1](optional): default value
    """
    if not character:
        return

    if not args:
        return

    key = args[0]
    default = None
    if len(args) > 1:
        default = args[1]

    return character.custom_attr.get(key, default)


def remove_attr(character, obj, *args):
    """
    Remove the character's attribute.
    args:
        args[0]: attribute key
    """
    if not character:
        return

    if not args:
        return

    key = args[0]
    character.custom_attr.remove(key)


def fight_mob(character, obj, *args):
    """
    Fight with specified target.

    Args:
        args[0]: mob's key
        args[1]: mob's level
        args[2]: optional fight's desc
    """
    if not character:
        return

    if not args:
        return

    key = args[0]

    level = 1
    if len(args) > 1:
        level = args[1]

    desc = ""
    if len(args) > 2:
        desc = args[2]

    character.attack_clone_target(key, level, desc)


def fight_target(character, obj, *args):
    """
    Fight with current target.

    Args:
        args[0]: optional fight's desc
    """
    if not character:
        return

    desc = ""
    if args:
        desc = args[0]

    character.attack_clone_target(obj.get_data_key(), obj.db.level, desc)