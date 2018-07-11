
"""
World location's field. Group rooms by areas.
"""

from django.contrib.admin.forms import forms


class ImageField(forms.CharField):
    """
    Image's field.
    """
    def __init__(self, image_type="image", *args, **kwargs):
        """

        Args:
            image_type: (string) image's type, could be "icon" or "image".
        """
        super(ImageField, self).__init__(*args, **kwargs)
        self.image_type = image_type

    def get_type(self):
        """
        Get image type.

        Return:
             (string) image type.
        """
        return self.image_type