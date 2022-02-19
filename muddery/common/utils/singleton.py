
"""
Base class of singleton objects.
"""

import threading


class Singleton(object):
    _instance_lock = threading.Lock()

    @classmethod
    def inst(cls):
        """
        Singleton object.
        """
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = cls()
        return cls._instance
