"""
Logging facilities

These are thin wrappers on logging facilities; logs
are all directed either to stdout or to $GAME_DIR/server/logs.

"""

from traceback import format_exc
import os
import threading
from django.conf import settings
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger(object):
    """
    The logger object.
    """
    _instance_lock = threading.Lock()

    def __init__(self, log_path, log_name, log_level):
        """
        Init the logger.
        """
        self.logger = self.setup_log(log_path, log_name, log_level)

    @classmethod
    def instance(cls, *args, **kwargs):
        """
        Singleton object.
        """
        if not hasattr(Logger, "_instance"):
            with Logger._instance_lock:
                if not hasattr(Logger, "_instance"):
                    Logger._instance = Logger(*args, **kwargs)
        return Logger._instance

    def setup_log(self, log_path, log_name, log_level):
        """
        Create a logger.
        """
        # Create the logging object.
        logger = logging.getLogger(log_name)

        # Set log level.
        logger.setLevel(log_level)
        logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

        # Divide logs by date.
        filepath = os.path.join(log_path, log_name)
        file_handler = TimedRotatingFileHandler(filename=filepath, when="MIDNIGHT", interval=1)
        file_handler.suffix = "%Y-%m-%d.log"

        # Set output format.
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] - %(message)s"
            )
        )
        logger.addHandler(file_handler)
        return logger

    def log_msg(self, msg):
        """
        Wrapper around log.msg call to catch any exceptions that might
        occur in logging. If an exception is raised, we'll print to
        stdout instead.

        Args:
            msg: The message that was passed to log.msg

        """
        try:
            self.logger.info(msg)
        except Exception:
            print("Exception raised while writing message to log. Original message: %s" % msg)

    def log_trace(self, errmsg=None):
        """
        Log a traceback to the log. This should be called from within an
        exception.

        Args:
            errmsg (str, optional): Adds an extra line with added info
                at the end of the traceback in the log.

        """
        trace_string = format_exc()
        try:
            if trace_string:
                for line in trace_string.splitlines():
                    self.logger.error("[::] %s" % line)
            if errmsg:
                try:
                    errmsg = str(errmsg)
                except Exception as e:
                    errmsg = str(e)
                for line in errmsg.splitlines():
                    self.logger.error("[EE] %s" % line)
        except Exception:
            self.logger.error("[EE] %s" % errmsg)

    def log_err(self, errmsg):
        """
        Prints/logs an error message to the server log.

        Args:
            errmsg (str): The message to be logged.

        """
        try:
            errmsg = str(errmsg)
        except Exception as e:
            errmsg = str(e)

        for line in errmsg.splitlines():
            self.logger.error("[EE] %s" % line)

    def log_warn(self, warnmsg):
        """
        Prints/logs any warnings that aren't critical but should be noted.

        Args:
            warnmsg (str): The message to be logged.

        """
        try:
            warnmsg = str(warnmsg)
        except Exception as e:
            warnmsg = str(e)

        for line in warnmsg.splitlines():
            self.logger.warning("[WW] %s" % line)

    def log_info(self, infomsg):
        """
        Prints any generic debugging/informative info that should appear in the log.

        infomsg: (string) The message to be logged.
        """
        try:
            infomsg = str(infomsg)
        except Exception as e:
            infomsg = str(e)

        for line in infomsg.splitlines():
            self.logger.info("[..] %s" % line)

    def log_dep(self, depmsg):
        """
        Prints a deprecation message.

        Args:
            depmsg (str): The deprecation message to log.
        """
        try:
            depmsg = str(depmsg)
        except Exception as e:
            depmsg = str(e)

        for line in depmsg.splitlines():
            self.logger.warning("[DP] %s" % line)

    def log_sec(self, secmsg):
        """
        Prints a security-related message.

        Args:
            secmsg (str): The security message to log.
        """
        try:
            secmsg = str(secmsg)
        except Exception as e:
            secmsg = str(e)

        for line in secmsg.splitlines():
            self.logger.info("[SS] %s" % line)


game_server_logger = Logger.instance(settings.LOG_DIR, settings.LOG_GAME_SERVER, settings.LOG_LEVEL)
game_editor_logger = Logger.instance(settings.LOG_DIR, settings.LOG_GAME_EDITOR, settings.LOG_LEVEL)
