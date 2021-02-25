
class Atomic(object):
    """
    Guarantee the atomic execution of a given block.
    """
    def __init__(self, catch):
        self.catch = catch

    def __enter__(self):
        self.catch.transaction()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.catch.commit()
        else:
            self.catch.rollback()
