"""
Default action scripts are in this model.
Action script functions must be compatible with this:

def func(character, obj, *args)
    args:
        character(object): a player character.
        obj(object): the player character's action target.
        args: other args.

"""

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

    character.skill.learn_skill(args[0])


def give_object(character, obj, *args):
    """
    Teach the character a skill.
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
