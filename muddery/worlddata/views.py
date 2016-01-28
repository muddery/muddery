
"""
This contains a simple view for rendering the webclient
page and serve it eventual static content.

"""
from __future__ import print_function

import os, tempfile
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.servers.basehttp import FileWrapper
from evennia.players.models import PlayerDB
from muddery.utils import exporter


@staff_member_required
def worldeditor(request):
    """
    World Editor page template loading.
    """
    if "export" in request.GET:
        return export_file(request)

    return render(request, 'worldeditor.html')


def export_file(request):
    """
    """
    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    # remove temp file
                    os.remove(file_name)
                    break

    # get data's zip
    zipfile_name = tempfile.mktemp()
    exporter.export_zip_all(zipfile_name)

    response = StreamingHttpResponse(file_iterator(zipfile_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="worlddata.zip"'

    return response


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
        return render(request, '404.html')


@staff_member_required
def export_worlddata(request):
    pass