
"""
This contains a simple view for rendering the webclient
page and serve it eventual static content.

"""
from __future__ import print_function

import tempfile, time
from django import http
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from evennia.utils import logger
from muddery.utils import utils
from muddery.utils.localized_strings_handler import _, LOCALIZED_STRINGS_HANDLER


@staff_member_required
def tools(request):
    """
    World Editor page template loading.
    """
    if "export_py_localized_strings" in request.GET:
        return export_py_localized_strings(request)
    elif "export_js_localized_strings" in request.GET:
        return export_js_localized_strings(request)

    return render(request, 'tools.html')


@staff_member_required
def export_py_localized_strings(request):
    """
    Export all unlicalized strings in files.
    """
    response = http.HttpResponseNotModified()

    try:
        # write to a file
        file = tempfile.TemporaryFile()
        
        # header
        file.write('"category","origin","local"\n')
        
        # get strings
        strings = utils.all_unlocalized_py_strings(True)
        
        for s in strings:
            if s[1]:
                file.write('"%s","%s",""\n' % (s[1], s[0]))
            else:
                file.write(',"%s",""\n' % (s[0]))

        file.seek(0)
        filename = time.strftime("strings_%Y%m%d_%H%M%S.csv", time.localtime())
        response = http.StreamingHttpResponse(utils.file_iterator(file))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % filename
    except Exception, e:
        message = "Can't export game data: %s" % e
        logger.log_tracemsg(message)

        file.close()
        return render(request, 'fail.html', {"message": message})

    return response
    

@staff_member_required
def export_js_localized_strings(request):
    """
    Export all unlicalized strings in files.
    """
    response = http.HttpResponseNotModified()

    try:
        # write to a file
        file = tempfile.TemporaryFile()
        
        # get strings
        strings = utils.all_unlocalized_js_strings(True)

        for s in strings:
            file.write('"%s": "",\n' % s)

        file.seek(0)
        filename = time.strftime("strings_%Y%m%d_%H%M%S.js", time.localtime())
        response = http.StreamingHttpResponse(utils.file_iterator(file))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % filename
    except Exception, e:
        message = "Can't export game data: %s" % e
        logger.log_tracemsg(message)

        file.close()
        return render(request, 'fail.html', {"message": message})

    return response

