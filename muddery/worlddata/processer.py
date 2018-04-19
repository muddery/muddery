"""
Decorators of web service controllers.

This decorator can add controllers to the controller dict for future usage.
"""

from __future__ import print_function

import json
from django.conf import settings
from django.http import HttpResponse
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

    def process(self, request):
        """
        Process a request by the func key.
        
        Args:
            request: HTTP request.
        """
        # check authentication
        if not request.user.is_authenticated:
            return self.response(-1, "No permission.")

        path = request.path_info
        if self.path_prefix:
            if path.find(self.path_prefix) == 0:
                path = path[len(self.path_prefix):]
        
        func = request.POST.get("func", "")
        args = request.POST.get("args", None)
        
        print("request: '%s' '%s' '%s'" % (path, func, args))

        function = REQUEST_MAPPING.get_function(path, func)
        if function:
            # call function
            try:
                result = function(args)
                response = self.response(0, result)
            except MudderyError, e:
                response = self.response(e.code, e.message)
        else:
            response = self.response(-1, "Can not find this API.")
        
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
        return HttpResponse(content, content_type="application/json")


PROCESSER = Processer(settings.WORLD_DATA_API_PATH)
