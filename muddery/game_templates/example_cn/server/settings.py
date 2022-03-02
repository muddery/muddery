"""
Game settings file.
"""
import logging


class ServerSettings(object):

    ######################################################################
    # Base server config
    ######################################################################

    # This is a security setting protecting against host poisoning
    # attacks.  It defaults to allowing all. In production, make
    # sure to change this to your actual host addresses/IPs.
    ALLOWED_HOST = "0.0.0.0"

    # The webserver sits behind a Portal proxy.
    WEBCLIENT_PORT = {WEBCLIENT_PORT}

    # Server-side websocket port to open for the webclient.
    GAME_SERVER_PORT = {GAME_SERVER_PORT}

    # Language code for this installation. All choices can be found here:
    # http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
    LANGUAGE_CODE = 'zh-Hans'

    # The log level
    LOG_LEVEL = logging.WARNING

    # Also print logs to the console.
    LOG_TO_CONSOLE = False

    ######################################################################
    # Default statement sets
    ######################################################################

    # Skill functions set
    SKILL_FUNC_SET = "statements.statement_func_set.SkillFuncSet"


    ###################################
    # AI modules
    ###################################
    AI_CHOOSE_SKILL = "ai.choose_skill.ChooseSkill"


    ######################################################################
    # Command settings
    ######################################################################

    # Determine how many commands per second a given Session is allowed
    # to send. Too high rate will drop the command and echo a warning.
    # To turn the limiter off, set to <= 0.
    MAX_COMMAND_RATE = 20

    # The warning to echo back to users if they send commands too fast
    COMMAND_RATE_WARNING = "您的操作太快了，请稍后重试。"

    # Determine how many specified commands per second a given Session is allowed
    # to send. Too high rate will drop the specified command and echo a warning.
    # To turn the limiter off, set to <= 0.
    SPECIAL_COMMAND_RATE = {{
        "traverse": {{
            "max_rate": 4,
            "message": "你太久没有锻炼了，走这点路就把你累得气喘吁吁，休息一下再走吧。",
        }}
    }}
