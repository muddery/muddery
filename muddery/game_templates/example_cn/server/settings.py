"""
Game settings file.
"""

# Use the defaults from Muddery
from muddery.server.default_settings import Settings as DefaultSettings


class Settings(DefaultSettings):

    ######################################################################
    # Base server config
    ######################################################################

    # This is a security setting protecting against host poisoning
    # attacks.  It defaults to allowing all. In production, make
    # sure to change this to your actual host addresses/IPs.
    ALLOWED_HOSTS = "['*']"

    # The webserver sits behind a Portal proxy.
    WEBCLIENT_PORT = 8000

    # Server-side websocket port to open for the webclient.
    WEBSERVER_PORT = 8001

    # Language code for this installation. All choices can be found here:
    # http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
    LANGUAGE_CODE = 'zh-Hans'


    ######################################################################
    # Default statement sets
    ######################################################################

    # Skill functions set
    SKILL_FUNC_SET = "statements.statement_func_set.SkillFuncSet"


    ###################################
    # AI modules
    ###################################
    AI_CHOOSE_SKILL = "ai.choose_skill.ChooseSkill"