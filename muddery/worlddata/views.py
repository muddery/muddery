
"""
This contains a simple view for rendering the webclient
page and serve it eventual static content.

"""
from __future__ import print_function

import os, tempfile
from django import http
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import logger
from muddery.utils import exporter
from muddery.utils import importer
from muddery.utils.builder import build_all


@staff_member_required
def worldeditor(request):
    """
    World Editor page template loading.
    """
    if "export" in request.GET:
        return export_file(request)
    elif "import" in request.FILES:
        return import_file(request)
    elif "apply" in request.POST:
        return apply_changes(request)

    return render(request, 'worldeditor.html')


@staff_member_required
def export_file(request):
    """
    Export game world files.
    """
    def file_iterator(file, chunk_size=512):
        while True:
            c = file.read(chunk_size)
            if c:
                yield c
            else:
                # remove temp file
                file.close()
                break

    response = http.HttpResponseNotModified()

    # get data's zip
    try:
        zipfile = tempfile.TemporaryFile()
        exporter.export_zip_all(zipfile)
        zipfile.seek(0)

        response = http.StreamingHttpResponse(file_iterator(zipfile))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="worlddata.zip"'
    except Exception, e:
        logger.log_tracemsg("Can't export world: %s" % e)
        response = http.HttpResponseServerError()

    return response


@staff_member_required
def import_file(request):
    """
    Import the game world from an uploaded zip file.
    """
    response = http.HttpResponseNotModified()
    file_obj = request.FILES.get("import", None)

    if file_obj:
        zipfile = tempfile.TemporaryFile()
        try:
            for chunk in file_obj.chunks():
                zipfile.write(chunk)
            importer.import_zip_all(zipfile)
        except Exception, e:
            logger.log_tracemsg("Can't import world: %s" % e)
            response = http.HttpResponseServerError()
        finally:
            zipfile.close()

    return response

@staff_member_required
def apply_changes(request):
    """
    Apply the game world's data.
    """
    try:
        # rebuild the world
        build_all()

        # reload
        SESSIONS.announce_all(" Server restarting ...")
        SESSIONS.server.shutdown(mode='reload')
    except Exception, e:
        ostring = "Can't build world: %s" % e
        logger.log_tracemsg(ostring)
        raise http.HttpResponseServerError

    return http.HttpResponse("Server is reloading...")


@staff_member_required
def editor(request):
    """
    World Editor page template loading.
    """
    try:
        path = request.path.split('/')
        name = path[-1]
        if not name:
            name = path[-2]
        return render(request, name + '.html')
    except:
        raise http.Http404


@staff_member_required
def export_worlddata(request):
    pass