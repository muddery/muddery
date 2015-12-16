"""
Example skills.
"""

def skill_example(caller, target, *args, **kwargs):
    """
    It is an example.
    """
    pass


def skill_heal(caller, target, effect=0, *args, **kwargs):
    """
    Heal the target, if target is None, heal the caller.
    """
    if effect <= 0:
        return

    if not caller:
        return

    target = caller

    if target:
        recover_hp = target.add_hp(effect)
        if recover_hp > 0:
            target.show_status()

    return [{"type": "healed",              # heal result
             "caller": caller.dbref,        # caller's dbref
             "target": target.dbref,        # target's dbref
             "effect": effect,              # effect
             "hp": target.db.hp,            # current hp of the target
             "max_hp": target.max_hp}]      # max hp of the target


def skill_hit(caller, target, effect=0, *args, **kwargs):
    """
    Hit the target.
    """
    if not caller:
        return

    if not target:
        return

    # calculate the damage
    damage = float(caller.attack) / (caller.attack + target.defence) * caller.attack
    damage = round(damage)
    
    # hurt target
    target.hurt(damage)

    return [{"type": "attacked",            # attack result
             "caller": caller.dbref,        # caller's dbref
             "target": target.dbref,        # target's dbref
             "effect": damage,              # effect
             "hp": target.db.hp,            # current hp of the target
             "max_hp": target.max_hp}]      # max hp of the target


def skill_increase_hp(caller, target, effect=0, *args, **kwargs):
    """
    Passive skill, increase the caller's max_hp.
    """
    if effect <= 0:
        return

    if not caller:
        return

    target = caller

    if target:
        caller.max_hp += effect
        hp = caller.db.hp + effect
        if hp > caller.max_hp:
            hp = caller.max_hp
        caller.db.hp = hp
