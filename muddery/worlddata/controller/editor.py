"""
Battle commands. They only can be used when a character is in a combat.
"""

from __future__ import print_function

from django.apps import apps
from django.conf import settings
from evennia.utils import logger
from muddery.worlddata.request_mapping import request_mapping
from muddery.worlddata.dao.skills_mapper import SkillsMapper


@request_mapping
def query_all_skills(args):
    """
    Query all skills.
    """
    return SkillsMapper.get_all()
