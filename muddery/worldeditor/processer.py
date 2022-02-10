"""
Decorators of web service controllers.

This decorator can add controllers to the controller dict for future usage.
"""

from muddery.common.networks import responses
from muddery.common.utils.exception import MudderyError, ERR
from muddery.worldeditor.mappings.request_set import RequestSet
from muddery.worldeditor.utils.logger import logger
from muddery.worldeditor.utils.auth import check_token


class Processor(object):
    """
    HTTP request processor.
    """
    def __init__(self, path_prefix=None):
        if path_prefix:
            if path_prefix[0] != "/":
                path_prefix = "/" + path_prefix

        self.path_prefix = path_prefix
        self.request_set = RequestSet()

    async def process(self, method, path, data, token=None):
        """
        Process a request by the func key.
        
        Args:
            request: HTTP request.
        """
        if method == "OPTIONS":
            return responses.empty_response()

        if self.path_prefix:
            if path.find(self.path_prefix) == 0:
                path = path[len(self.path_prefix):]

        func = data.get("func", "")
        args = data.get("args", {})

        logger.log_info("[REQUEST] '%s' '%s' '%s'" % (path, func, args))
        print("[REQUEST] '%s' '%s' '%s'" % (path, func, args))

        processor = self.request_set.get(path, func)
        if not processor:
            logger.log_err("Can not find API: %s %s" % (path, func))
            return responses.error_response(ERR.no_api, msg="Can not find API: %s %s" % (path, func), status=400)

        # check authentication
        if processor.login and not check_token(token):
            logger.log_err("Need authentication.")
            return responses.error_response(ERR.no_authentication, msg="Need authentication.", status=401)

        # check staff
        #if processor.staff and not request.user.is_staff and not request.user.is_superuser:
        #    return responses.error_response(ERR.no_permission, msg="No permission.")

        # call function
        try:
            response = await processor.func(args)
        except MudderyError as e:
            logger.log_err("Error: %s, %s" % (e.code, e))
            response = responses.error_response(e.code, msg=str(e), data=e.data, status=200)
        except Exception as e:
            logger.log_trace("Error: %s" % e)
            response = responses.error_response(ERR.internal, msg=str(e))

        return response
