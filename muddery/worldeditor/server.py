
import traceback
import threading
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from muddery.server.utils.utils import class_from_path
from muddery.server.utils.singleton import Singleton
from muddery.server.service.command_handler import CommandHandler
from muddery.worldeditor.database.db_manager import DBManager
from muddery.worldeditor.dao.accounts import Accounts
from muddery.worldeditor.processer import Processor


class Server(Singleton):
    """
    The game world.
    """
    _instance_lock = threading.Lock()

    class ClassProperty:
        def __init__(self, method):
            self.method = method

        def __get__(self, instance, owner):
            return self.method(owner)

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

        self.db_connected = False
        self.connect_db()
        self.check_admin()
        self.processor = Processor(settings.WORLD_EDITOR_API_PATH)

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
        # if Accounts.inst().count() == 0:
        #    # Add a default ADMIN account
        #    Accounts.inst().add("admin", make_password("administrator"), "ADMIN")

        if User.objects.all().count() == 0:
            # Add a default ADMIN account
            User.objects.create_user(username='admin', password='administrator')

    @csrf_exempt
    def handle_request(self, request):
        return self.processor.process(request)
