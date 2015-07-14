"""
Skill handler.
"""

from django.conf import settings


def get_skill(skill_name):
    """
    Get skill function.
    """
    skill_folder = settings.SKILL_FOLDER + "."
    
    for file_name in settings.SKILL_FILES:
        skill_model = __import__(skill_folder + file_name, globals(), locals(), [file_name])

        if hasattr(skill_model, skill_name):
            return getattr(skill_model, skill_name)


def cast_skill(skill_name, caller, target, **kwargs):
    """
    Cast a skill.
    """
    skill = get_skill(skill_name)
    if skill:
        skill(caller, target, **kwargs)
