
from muddery.common.utils.crypto import RSA as CommonRSA
from muddery.common.utils.singleton import Singleton
from muddery.server.settings import SETTINGS


class RSA(CommonRSA, Singleton):
    def __init__(self):
        super(RSA, self).__init__()
        self.load_private_key_file(SETTINGS.RSA_PRIVATE_KEY_FILE)
