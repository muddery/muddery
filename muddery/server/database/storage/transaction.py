
from muddery.server.database.storage.base_transaction import BaseTransaction


class Transaction(BaseTransaction):
    """
    Guarantee the transaction execution of a given block.
    """
    def __init__(self, storage):
        super(Transaction, self).__init__()
        self.storage = storage

    def __enter__(self):
        self.storage.transaction()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.storage.commit()
        else:
            self.storage.rollback()
