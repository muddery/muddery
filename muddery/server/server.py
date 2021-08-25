

class Server(object):
    """
    The game world.
    """
    class classproperty:
        def __init__(self, method):
            self.method = method

        def __get__(self, instance, owner):
            return self.method(owner)

    @classmethod
    def create_the_world(cls):
        """
        Create the whole game world.
        :return:
        """
        from muddery.server.mappings.element_set import ELEMENT
        world = ELEMENT("WORLD")()
        world.setup_element("")
        cls._world_data = world

    # @property system stores object's data.
    @classproperty
    def world(cls):
        """
        A system_data store. Everything stored to this is from the
        world data. It will be reset every time when the object init .
        Syntax is same as for the _get_db_holder() method and
        property, e.g. obj.system.attr = value etc.
        """
        try:
            return cls._world_data
        except AttributeError:
            cls.create_the_world()
            return cls._world_data
