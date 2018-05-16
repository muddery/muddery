"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from evennia.utils import logger
from muddery.worlddata.dao import model_mapper
from muddery.worlddata.dao import common_mappers as cm


def get_all_objects():
    """
    Get all objects.
    """
    choices = []
    for data in model_mapper.get_objects_models():
        objects = data.objects.all()
        choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in objects])

    return choices
    
    
def get_all_pocketable_objects():
    """
    Get all objects that can be put in player's pockets.
    """
    # available objects are common objects, foods skill books or equipments
    objects = cm.COMMON_OBJECTS.all()
    choices = [(obj.key, obj.name + " (" + obj.key + ")") for obj in objects]

    foods = cm.FOODS.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in foods])

    skill_books = cm.SKILL_BOOKS.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in skill_books])

    equipments = cm.EQUIPMENTS.objects.all()
    choices.extend([(obj.key, obj.name + " (" + obj.key + ")") for obj in equipments])

    return choices

