"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # load data
    from muddery.server.database.worlddata.worlddata import WorldData
    WorldData.reload()

    # reset settings
    from muddery.server.utils.game_settings import GAME_SETTINGS
    GAME_SETTINGS.reset()

    # reload local strings
    from muddery.server.utils.localized_strings_handler import LOCALIZED_STRINGS_HANDLER
    LOCALIZED_STRINGS_HANDLER.reload()

    # reset default locations
    from muddery.server.utils import builder
    builder.reset_default_locations()
    
    # clear dialogues
    from muddery.server.utils.dialogue_handler import DIALOGUE_HANDLER
    DIALOGUE_HANDLER.clear()
    
    # reload equipment types
    from muddery.server.utils.equip_type_handler import EQUIP_TYPE_HANDLER
    EQUIP_TYPE_HANDLER.reload()

    # localize model fields
    from muddery.server.utils.localiztion_handler import localize_model_fields
    localize_model_fields()
    
    # load condition descriptions
    from muddery.server.utils.desc_handler import DESC_HANDLER
    DESC_HANDLER.reload()

    # load honours
    from muddery.server.database.gamedata.honours_mapper import HONOURS_MAPPER
    HONOURS_MAPPER.reload()


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass
