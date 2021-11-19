"""
Logging facilities

These are thin wrappers on top of Twisted's logging facilities; logs
are all directed either to stdout or to $GAME_DIR/server/logs.

"""
import time
from datetime import datetime
from traceback import format_exc
from twisted.python import log


# logging overrides
def timeformat(when=None):
    """
    This helper function will format the current time in the same
    way as the twisted logger does, including time zone info. Only
    difference from official logger is that we only use two digits
    for the year and don't show timezone for CET times.

    Args:
        when (int, optional): This is a time in POSIX seconds on the form
            given by time.time(). If not given, this function will
            use the current time.

    Returns:
        timestring (str): A formatted string of the given time.
    """
    when = when if when else time.time()

    # time zone offset: UTC - the actual offset
    tz_offset = datetime.utcfromtimestamp(when) - datetime.fromtimestamp(when)
    tz_offset = tz_offset.days * 86400 + tz_offset.seconds
    # correct given time to utc
    when = datetime.utcfromtimestamp(when - tz_offset)

    if tz_offset == 0:
        tz = ""
    else:
        tz_hour = abs(int(tz_offset // 3600))
        tz_mins = abs(int(tz_offset // 60 % 60))
        tz_sign = "-" if tz_offset >= 0 else "+"
        tz = "%s%02d%s" % (tz_sign, tz_hour, (":%02d" % tz_mins if tz_mins else ""))

    return "%d-%02d-%02d %02d:%02d:%02d%s" % (
        when.year - 2000,
        when.month,
        when.day,
        when.hour,
        when.minute,
        when.second,
        tz,
    )


def log_msg(msg):
    """
    Wrapper around log.msg call to catch any exceptions that might
    occur in logging. If an exception is raised, we'll print to
    stdout instead.

    Args:
        msg: The message that was passed to log.msg

    """
    try:
        log.msg(msg)
    except Exception:
        print("Exception raised while writing message to log. Original message: %s" % msg)


def log_trace(errmsg=None):
    """
    Log a traceback to the log. This should be called from within an
    exception.

    Args:
        errmsg (str, optional): Adds an extra line with added info
            at the end of the traceback in the log.

    """
    tracestring = format_exc()
    try:
        if tracestring:
            for line in tracestring.splitlines():
                log.msg("[::] %s" % line)
        if errmsg:
            try:
                errmsg = str(errmsg)
            except Exception as e:
                errmsg = str(e)
            for line in errmsg.splitlines():
                log_msg("[EE] %s" % line)
    except Exception:
        log_msg("[EE] %s" % errmsg)


def log_err(errmsg):
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
        log_msg("[EE] %s" % line)


def log_warn(warnmsg):
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
        log_msg("[WW] %s" % line)


def log_info(infomsg):
    """
    Prints any generic debugging/informative info that should appear in the log.

    infomsg: (string) The message to be logged.
    """
    try:
        infomsg = str(infomsg)
    except Exception as e:
        infomsg = str(e)
    for line in infomsg.splitlines():
        log_msg("[..] %s" % line)


def log_dep(depmsg):
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
        log_msg("[DP] %s" % line)


def log_sec(secmsg):
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
        log_msg("[SS] %s" % line)

