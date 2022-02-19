
class DictRecord(object):
    """
    Record object. Use attributes to access dict values.
    """
    def __init__(self, data):
        """
        Args:
            data: (dict) a dict of data.
        """
        object.__setattr__(self, "_data", data)

    def __getattribute__(self, attr_name):
        try:
            return object.__getattribute__(self, "_data")[attr_name]
        except KeyError:
            raise AttributeError("Can not find field %s." % attr_name)

    def __setattr__(self, attr_name, value):
        raise Exception("Cannot assign directly to record attributes!")

    def __delattr__(self, attr_name):
        raise Exception("Cannot delete record attributes!")
