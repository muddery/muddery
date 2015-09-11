"""
Skills
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
    Heal the target, if target is None, heal the caller.
    """
    if not caller:
        return

    if not target:
        return

    damage = float(caller.attack) / (caller.attack + target.defence) * caller.attack
    damage = round(damage)
    target.hurt(damage)

    return {"character": target.dbref,
            "hurt": damage,
            "hp": target.db.hp,
            "max_hp": target.max_hp}
