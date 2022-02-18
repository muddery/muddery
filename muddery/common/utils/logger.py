"""
Logging facilities

These are thin wrappers on logging facilities; logs
are all directed either to stdout or to $GAME_DIR/server/logs.

"""
import sys
from traceback import format_exc
import os
import threading
import logging
from logging.handlers import TimedRotatingFileHandler


class Logger(object):
    """
    The logger object.
    """
    def __init__(self, log_name, log_file, log_level, log_to_console):
        """
        Init the logger.
        """
        self.logger = self.setup_log(log_name, log_file, log_level, log_to_console)

    def setup_log(self, log_name, log_file, log_level, log_to_console):
        """
        Create a logger.
        """
        # Create the logging object.
        logger = logging.getLogger(log_name)

        # Set log level.
        logger.setLevel(log_level)
        logging.getLogger('apscheduler.executors.default').setLevel(log_level)

        # Divide logs by date.
        file_handler = TimedRotatingFileHandler(filename=log_file, when="MIDNIGHT", interval=1)
        file_handler.suffix = "%Y-%m-%d.log"

        # Set output format.
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] - %(message)s"))

        logger.addHandler(file_handler)

        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter("[%(asctime)s] - %(message)s"))
            logger.addHandler(console_handler)

        return logger

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
        except Exception as e:
            self.logger.error("[EE] %s" % errmsg)

    def log_critical(self, msg):
        """
        Prints/logs a critical message to the server log.

        Args:
            msg (str): The message to be logged.

        """
        try:
            msg = str(msg)
        except Exception as e:
            msg = str(e)

        for line in msg.splitlines():
            self.logger.critical("[CC] %s" % line)

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
        Prints any generic informative info that should appear in the log.

        infomsg: (string) The message to be logged.
        """
        try:
            infomsg = str(infomsg)
        except Exception as e:
            infomsg = str(e)

        for line in infomsg.splitlines():
            self.logger.info("[..] %s" % line)

    def log_debug(self, msg):
        """
        Prints any generic debugging info that should appear in the log.

        infomsg: (string) The message to be logged.
        """
        try:
            msg = str(msg)
        except Exception as e:
            msg = str(e)

        for line in msg.splitlines():
            self.logger.debug("[DD] %s" % line)

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
