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

    if target:
        damage = caller.attack / (caller.attack + target.defence) * caller.attack
        target.hurt(damage)
        if damage > 0:
            target.show_status()
