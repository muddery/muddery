"""
Handles a character's attributes used in statements.
"""

import weakref


class StatementAttributeHandler(object):
    """
    Handles a character's attributes used in statements.
    """
    def __init__(self, owner):
        """
        Initialize handler.
        """
        self.owner = self.owner = weakref.proxy(owner)

    def set(self, key, value=None):
        """
        Set an attribute.
        """
        attributes = self.owner.load("attributes", {})
        attributes[key] = value
        self.owner.save("attributes", attributes)

    def get(self, key, default=None):
        """
        Get an attribute. If the key does not exist, returns default.
        """
        attributes = self.owner.load("attributes", {})
        if key not in attributes:
            return default

        return attributes[key]

    def remove(self, key):
        """
        Remove an attribute

        Returns:
            Can remove.
        """
        attributes = self.owner.load("attributes", {})
        if key not in attributes:
            return False

        del attributes[key]
        self.owner.save("attributes", attributes)
        return True

    def has(self, key):
        """
        Does this attribute exist.
        """
        attributes = self.owner.load("attributes", {})
        return key in attributes

    def check_value(self, key, value):
        """
        Does this attribute match the value.
        """
        attributes = self.owner.load("attributes", {})
        if key not in attributes:
            return False

        return attributes[key] == value
