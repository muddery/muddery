
import traceback
from muddery.common.utils.singleton import Singleton
from muddery.common.utils.password import hash_password, make_salt
from muddery.worldeditor.settings import SETTINGS
from muddery.server.database.worlddata_db import WorldDataDB
from muddery.worldeditor.database.worldeditor_db import WorldEditorDB
from muddery.worldeditor.dao.accounts import Accounts
from muddery.worldeditor.processer import Processor


class Server(Singleton):
    """
    The game editor server.
    """
    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

        self.db_connected = False
        self.processor = None

    def init(self):
        self.connect_db()
        self.processor = Processor()

    def connect_db(self):
        """
        Create the db connection.
        """
        if self.db_connected:
            return

        try:
            # init world data
            WorldDataDB.inst().connect()
            WorldEditorDB.inst().connect()
        except Exception as e:
            traceback.print_exc()
            raise

        self.db_connected = True

    def check_admin(self):
        """
        Create an administrator account.
        """
        return Accounts.inst().count() == 0

    def create_admin(self, username, password):
        """
        Create an administrator account.
        """
        # Add a default ADMIN account
        salt = make_salt()
        password = hash_password(password, salt)
        try:
            Accounts.inst().add(username, password, salt, "ADMIN")
        except Exception as e:
            print(e)

    async def handle_request(self, method, path, data, request, token=None):
        return await self.processor.process(method, path, data, request, token)
