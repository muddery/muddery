
"""
World location's field. Group rooms by areas.
"""

from wtforms import widgets, fields


class Location(widgets.TextInput):
    pass


class LocationField(fields.SelectField):
    """
    World location's field.
    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            image_type: (string) image's type, could be "icon" or "image".
        """
        super(LocationField, self).__init__(widget=Location, *args, **kwargs)
