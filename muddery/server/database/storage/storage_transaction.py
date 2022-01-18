
import weakref
from muddery.server.database.storage.base_transaction import BaseTransaction


class StorageTransaction(BaseTransaction):
    """
    Guarantee the transaction execution of a given block.
    """
    def __init__(self, storage):
        super(StorageTransaction, self).__init__()
        self.storage = weakref.proxy(storage)

    def __enter__(self):
        self.storage.transction_begin()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.storage.transction_commit()
        else:
            self.storage.transction_rollback()
