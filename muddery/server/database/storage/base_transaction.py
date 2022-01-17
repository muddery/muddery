
class BaseTransaction(object):
    """
    Guarantee the transaction execution of a given block.
    """
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass
