"""
Decorators of web service controllers.

This decorator can add controllers to the controller dict for future usage.
"""

from __future__ import print_function

import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.worlddata.request_mapping import REQUEST_MAPPING
import muddery.worlddata.controllers


class Processer(object):
    """
    HTTP request processer.
    """
    def __init__(self, path_prefix=None):
        if path_prefix:
            if path_prefix[0] != "/":
                path_prefix = "/" + path_prefix

        self.path_prefix = path_prefix

    @csrf_exempt
    def process(self, request):
        """
        Process a request by the func key.
        
        Args:
            request: HTTP request.
        """
        if request.method == "OPTIONS":
            return self.response()
            
        path = request.path_info
        if self.path_prefix:
            if path.find(self.path_prefix) == 0:
                path = path[len(self.path_prefix):]

        data = {}
        try:
            data = json.loads(request.body)
        except Exception, e:
            pass
        
        func = data.get("func", "")
        args = data.get("args", None)
        
        print("request: '%s' '%s' '%s'" % (path, func, args))

        func_data = REQUEST_MAPPING.get_function(path, func)
        if not func_data:
            return self.response(-1, "Can not find this API.")

        # check authentication
        if func_data["login"] and not request.user.is_authenticated:
            return self.response(-1, "Need authentication.")

        # check staff
        if func_data["staff"] and not request.user.is_staff and not request.user.is_superuser:
            return self.response(-1, "No permission.")

        # call function
        try:
            function = func_data["func"]
            result = function(args, request)
            response = self.response(0, result)
        except MudderyError, e:
            logger.log_errmsg("Error: %s, %s" % (e.code, e.message))
            response = self.response(e.code, e.message)
        except Exception, e:
            logger.log_errmsg("Error: %s" % e.message)
            response = self.response(-1, e.message)

        return response

    def response(self, code=0, data=None):
        """
        Generate HTTP response.

        Args:
            code: respond code.
            data: respond data.
        """
        content = json.dumps({"code": code,
                              "result": data})
        response = HttpResponse(content, content_type="application/json")
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST,GET,OPTIONS"
        response["Access-Control-Allow-Headers"] = "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type"
        return response


PROCESSER = Processer(settings.WORLD_DATA_API_PATH)

