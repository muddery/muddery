
import weakref


class Transaction(object):
    """
    Guarantee the transaction execution of a given block.
    """
    def __init__(self, storage):
        self.storage = weakref.proxy(storage)

    def __enter__(self):
        self.storage.transaction_enter()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.storage.transaction_success(exc_type, exc_value, traceback)
        else:
            self.storage.transaction_failed(exc_type, exc_value, traceback)
