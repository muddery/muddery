
import weakref
from muddery.server.database.storage.base_transaction import BaseTransaction


class CacheTransaction(BaseTransaction):
    """
    Guarantee the transaction execution of a given block.
    """
    def __init__(self, storage):
        super(CacheTransaction, self).__init__()
        self.storage = weakref.proxy(storage)
        self.dirty_categories = set()

    def __enter__(self):
        self.dirty_categories = set()

    def set_dirty_category(self, category: str) -> None:
        self.dirty_categories.add(category)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.dirty_categories = set()
        else:
            # Remove dirty categories, so they can get correct values from the storage.
            for category in self.dirty_categories:
                self.storage.delete_category(category)
