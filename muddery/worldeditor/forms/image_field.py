
"""
Image's field.
"""

from wtforms import widgets, fields


class ImageInput(widgets.TextInput):
    pass


class ImageField(fields.StringField):
    """
    Image's field.
    """
    def __init__(self, image_type="image", *args, **kwargs):
        """
        Args:
            image_type: (string) image's type, could be "icon" or "image".
        """
        super(ImageField, self).__init__(widget=ImageInput(), *args, **kwargs)
        self.image_type = image_type

    def image_type(self):
        """
        Get image type.

        Return:
             (string) image type.
        """
        return self.image_type
