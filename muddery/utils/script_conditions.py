"""
Default condition scripts are in this model.
Condition script functions must be compatible with this:

def func(character, obj, *args)
    args:
        character(object): a player character.
        obj(object): the player character's action target.
        args: other args.

The return value must be a boolean value.

"""

import random

def example(caller, obj, *args):
    """
    This is an example.
    """
    return True


def is_quest_in_progress(character, obj, *args):
    """
    If the character is doing specified quest.
    args: quest's key
    """
    if not character:
        return False

    if not args:
        return False

    return character.quest_handler.is_in_progress(args[0])


def can_provide_quest(character, obj, *args):
    """
    If can provide specified quest to the character.
    args: quest's key
    """
    if not character:
        return False

    if not args:
        return False

    return character.quest_handler.can_provide(args[0])


def is_quest_completed(character, obj, *args):
    """
    If specified quest is completed.
    args: quest's key
    """
    if not character:
        return False

    if not args:
        return False

    return character.quest_handler.is_completed(args[0])


def have_object(character, obj, *args):
    """
    If the character has specified object.
    args: object's key
    """
    for item in character.contents:
        if item.get_data_key() == args[0]:
            return True
    return False


def has_attr(character, obj, *args):
    """
    Does this attribute exist.
    args:
        args[0]: attribute key
    """
    if not character:
        return False

    if not args:
        return False

    key = args[0]
    return character.custom_attr.has(key)


def is_attr(character, obj, *args):
    """
    Does this attribute match the value.
    args:
        args[0]: attribute key
        args[1]: attribute value
    """
    if not character:
        return False

    if not args:
        return False

    if len(args) < 2:
        return False

    key = args[0]
    value = args[1]
    return character.custom_attr.is_value(key, value)


def odd(character, obj, *args):
    """
    If a random number matches the odd.
    Args:
        character: no use
        obj: no use
        args[0]: (float) an odd number between 0 and 1

    Returns:
        (bool) If a random number matches the odd.
    """
    if not args:
        return False

    if len(args) < 1:
        return False

    return random.random() < args[0]


def rand(character, obj, *args):
    """
    Get a random number.

    Args:
        character: no use
        obj: no use
        args[0]: (float) the bound of the random number
        args[1]: (float) the bound of the random number

    Returns:
        (float) a random number between args[0] and args[1]
                if only give one args, the random number will between args[0] and 0
    """
    if not args:
        return 0

    if len(args) < 1:
        return 0

    bound1 = args[0]
    bound2 = 0
    if len(args) > 1:
        bound2 = args[1]

    return random.uniform(bound1, bound2)


def randint(character, obj, *args):
    """
    Get a random integer number.

    Args:
        character: no use
        obj: no use
        args[0]: (int) the bound of the random number
        args[1]: (int) the bound of the random number

    Returns:
        (int) a random number between args[0] and args[1]
             if only give one args, the random number will between args[0] and 0
    """
    if not args:
        return 0

    if len(args) < 1:
        return 0

    bound1 = args[0]
    bound2 = 0
    if len(args) > 1:
        bound2 = args[1]

    return random.randint(bound1, bound2)
