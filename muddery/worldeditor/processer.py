"""
Decorators of web service controllers.

This decorator can add controllers to the controller dict for future usage.
"""

import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from muddery.server.utils.logger import logger
from muddery.server.utils.exception import MudderyError, ERR
from muddery.worldeditor.mappings.request_set import RequestSet
import muddery.worldeditor.controllers
from muddery.worldeditor.utils.response import error_response


class Processor(object):
    """
    HTTP request processer.
    """
    def __init__(self, path_prefix=None):
        if path_prefix:
            if path_prefix[0] != "/":
                path_prefix = "/" + path_prefix

        self.path_prefix = path_prefix
        self.request_set = RequestSet()

    @csrf_exempt
    def process(self, request):
        """
        Process a request by the func key.
        
        Args:
            request: HTTP request.
        """
        if request.method == "OPTIONS":
            return HttpResponse()
            
        path = request.path_info
        if self.path_prefix:
            if path.find(self.path_prefix) == 0:
                path = path[len(self.path_prefix):]

        data = {}
        func = ""
        args = {}

        if request.POST:
            data = request.POST.dict()
            print("data: %s" % data)
            func = data.get("func", "")
            args_text = data.get("args", None)
            if args_text:
                args = json.loads(args_text)

        if not data:
            try:
                data = json.loads(request.body)
                func = data.get("func", "")
                args = data.get("args", {})
            except Exception as e:
                logger.log_err("Parse request body error: %s" % e)
                pass

        logger.log_info("[REQUEST] '%s' '%s' '%s'" % (path, func, args))

        processor = self.request_set.get(path, func)
        if not processor:
            logger.log_err("Can not find API: %s %s" % (path, func))
            return error_response(ERR.no_api, msg="Can not find API: %s %s" % (path, func))

        # check authentication
        if processor.login and not request.user.is_authenticated:
            logger.log_err("Need authentication.")
            return error_response(ERR.no_authentication, msg="Need authentication.")

        # check staff
        #if processor.staff and not request.user.is_staff and not request.user.is_superuser:
        #    return error_response(ERR.no_permission, msg="No permission.")

        # call function
        try:
            response = processor.func(args, request)
        except MudderyError as e:
            logger.log_err("Error: %s, %s" % (e.code, e))
            response = error_response(e.code, msg=str(e), data=e.data)
        except Exception as e:
            logger.log_trace("Error: %s" % e)
            response = error_response(ERR.internal, msg=str(e))

        logger.log_info("[RESPOND] '%s' '%s'" % (response.status_code, response.content))

        return response
