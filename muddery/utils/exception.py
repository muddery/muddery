"""
Define custom exception.
"""

class MudderyError(Exception):
    """
    Define custom exception.
    
    MudderyError(<Error Message>) or
    MudderyError(<Error Code>, <Error Message>, data=<Error Data>)
    """
    def __init__(self, *args, **kwargs):
        self.code = -1
        self.data = None

        if len(args) == 0:
            super(MudderyError, self).__init__()
        elif len(args) == 1:
            super(MudderyError, self).__init__(args[0])
        else:
            super(MudderyError, self).__init__(args[1])
            self.code = args[0]
            self.data = kwargs.get("data")


class ERR(object):
    """
    Error codes.
    """
    no_error = 0

    unknown = -1

    internal = 10000

    no_api = 10001

    no_authentication = 10002

    no_permission = 10003

    missing_args = 10004

    no_table = 10005

    invalid_form = 10006

    upload_error = 10007

    import_data_error = 10008

    download_error = 10009

    export_data_error = 10010

    build_world_error = 10011

    upload_image_exist = 10012

    no_data = 10013

    invalid_input = 10014


