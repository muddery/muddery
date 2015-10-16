"""
Example skills.
"""

def skill_example(caller, target, *args, **kwargs):
    """
    It is an example.
    """
    print "caller: %s" % caller
    print "target: %s" % target
    print args
    print kwargs


def skill_heal(caller, target, effect=0, *args, **kwargs):
    """
    Heal the target, if target is None, heal the caller.
    """
    if effect <= 0:
        return

    if not target:
        target = caller

    if target:
        recover_hp = target.add_hp(effect)
        if recover_hp > 0:
            target.show_status()


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
             "hurt": damage,                # damage
             "hp": target.db.hp,            # current hp of the target
             "max_hp": target.max_hp}]      # max hp of the target
