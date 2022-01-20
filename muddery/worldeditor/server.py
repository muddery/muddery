
import traceback
from muddery.server.utils.singleton import Singleton
from muddery.server.utils.password import hash_password, make_salt
from muddery.worldeditor.settings import SETTINGS
from muddery.worldeditor.database.db_manager import DBManager
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
        self.check_admin()
        self.processor = Processor(SETTINGS.WORLD_EDITOR_API_PATH)

    def connect_db(self):
        """
        Create the db connection.
        """
        if self.db_connected:
            return

        try:
            DBManager.inst().connect()
            DBManager.inst().create_tables()
            self.db_connected = True
        except Exception as e:
            traceback.print_exc()
            raise

    def check_admin(self):
        """
        Create an administrator account.
        """
        if Accounts.inst().count() == 0:
            # Add a default ADMIN account
            salt = make_salt()
            password = hash_password(SETTINGS.ADMIN_PASSWORD, salt)
            Accounts.inst().add(SETTINGS.ADMIN_NAME, password, salt, "ADMIN")

    def handle_request(self, method, path, data, token=None):
        return self.processor.process(method, path, data, token)
