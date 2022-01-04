
class MemoryRecord(object):
    """
    Record object. Use attributes to access record fields.
    """
    def __init__(self, fields, data):
        """
        Args:
            fields: (dict) a dict of field names and data positions.
            data: (list) a list of records. A record is a list too.
                  Data's order in a record must be the same as the position of fields dict.
        """
        object.__setattr__(self, "_fields", fields)
        object.__setattr__(self, "_records", data)

    def __getattribute__(self, attr_name):
        try:
            pos = object.__getattribute__(self, "_fields")[attr_name]
        except KeyError:
            raise AttributeError("Can not find field %s." % attr_name)
        return object.__getattribute__(self, "_records")[pos]

    def __setattr__(self, attr_name, value):
        raise Exception("Cannot assign directly to record attributes!")

    def __delattr__(self, attr_name):
        raise Exception("Cannot delete record attributes!")
