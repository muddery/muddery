
"""
This contains a simple view for rendering the webclient
page and serve it eventual static content.

"""
from __future__ import print_function

import tempfile, time, json, re
from django import http
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from evennia.server.sessionhandler import SESSIONS
from evennia.utils import logger
from muddery.utils import exporter
from muddery.utils import importer
from muddery.utils.builder import build_all
from muddery.utils.localized_strings_handler import LS
from muddery.utils.game_settings import CLIENT_SETTINGS
from muddery.worlddata.editor import page_view
from muddery.worlddata.editor.form_view import FormView
from muddery.worlddata.editor.single_form_view import SingleFormView
from muddery.worlddata.editor.relative_view import RelativeView
from muddery.worlddata.editor.dialogue_view import DialogueView
from muddery.worlddata.editor.dialogue_sentence_view import DialogueSentenceView
from muddery.worlddata.editor.dialogue_chain_view import DialogueChainView
from muddery.worlddata.editor.dialogue_chain_image import DialogueChainImage


@staff_member_required
def worldeditor(request):
    """
    World Editor page template loading.
    """
    if "export_game_data" in request.GET:
        return export_game_data(request)
    elif "export_resources" in request.GET:
        return export_resources(request)
    elif "import_game_data" in request.FILES:
        return import_game_data(request)
    elif "import_resources" in request.FILES:
        return import_resources(request)
    elif "apply" in request.POST:
        return apply_changes(request)

    return render(request, 'worldeditor.html')


@staff_member_required
def export_game_data(request):
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
    zipfile = None
    try:
        zipfile = tempfile.TemporaryFile()
        exporter.export_zip_all(zipfile)
        zipfile.seek(0)

        filename = time.strftime("worlddata_%Y%m%d_%H%M%S.zip", time.localtime())
        response = http.StreamingHttpResponse(file_iterator(zipfile))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % filename
    except Exception, e:
        if zipfile:
            zipfile.close()
        message = "Can't export game data: %s" % e
        logger.log_tracemsg(message)
        return render(request, 'fail.html', {"message": message})

    return response


@staff_member_required
def export_resources(request):
    """
    Export resource files.
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
    zipfile = None
    try:
        zipfile = tempfile.TemporaryFile()
        exporter.export_resources(zipfile)
        zipfile.seek(0)

        filename = time.strftime("resources_%Y%m%d_%H%M%S.zip", time.localtime())
        response = http.StreamingHttpResponse(file_iterator(zipfile))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % filename
    except Exception, e:
        if zipfile:
            zipfile.close()
        message = "Can't export resources: %s" % e
        logger.log_tracemsg(message)
        return render(request, 'fail.html', {"message": message})

    return response


@staff_member_required
def import_game_data(request):
    """
    Import the game world from an uploaded zip file.
    """
    response = http.HttpResponseNotModified()
    file_obj = request.FILES.get("import_game_data", None)

    if file_obj:
        zipfile = tempfile.TemporaryFile()
        try:
            for chunk in file_obj.chunks():
                zipfile.write(chunk)
            importer.import_zip_all(zipfile)
        except Exception, e:
            zipfile.close()
            logger.log_tracemsg("Cannot import game data: %s" % e)
            return render(request, 'fail.html', {"message": str(e)})

        zipfile.close()

    return render(request, 'success.html', {"message": "World data imported!"})


@staff_member_required
def import_resources(request):
    """
    Import resources from an uploaded zip file.
    """
    response = http.HttpResponseNotModified()
    file_obj = request.FILES.get("import_resources", None)

    if file_obj:
        zipfile = tempfile.TemporaryFile()
        try:
            for chunk in file_obj.chunks():
                zipfile.write(chunk)
            importer.import_resources(zipfile)
        except Exception, e:
            zipfile.close()
            logger.log_tracemsg("Cannot import resources: %s" % e)
            return render(request, 'fail.html', {"message": str(e)})

        zipfile.close()

    return render(request, 'success.html', {"message": "Resources imported!"})


@staff_member_required
def apply_changes(request):
    """
    Apply the game world's data.
    """
    try:
        # rebuild the world
        build_all()

        # send client settings
        CLIENT_SETTINGS.reset()
        text = json.dumps({"settings": CLIENT_SETTINGS.all_values()})
        SESSIONS.announce_all(text)

        # restart the server
        SESSIONS.announce_all(" Server restarting ...")
        SESSIONS.server.shutdown(mode='reload')
    except Exception, e:
        message = "Can't build world: %s" % e
        logger.log_tracemsg(message)
        return render(request, 'fail.html', {"message": message})

    return render(request, 'success.html', {"message": LS("Data applied.")})


@staff_member_required
def editor(request):
    """
    World Editor page template loading.
    """
    try:
        name = re.sub(r"^/worlddata/editor/", "", request.path)
        return render(request, name, {"self": request.get_full_path()})
    except Exception, e:
        logger.log_tracemsg(e)
        raise http.Http404


@staff_member_required
def list_view(request):
    try:
        if "_back" in request.POST:
            return page_view.quit_list(request)
        else:
            return page_view.view_list(request)
    except Exception, e:
        logger.log_tracemsg("Invalid view request: %s" % e)

    raise http.Http404


@staff_member_required
def view_form(request):
    try:
        view = get_view(request)
        if view.is_valid():
            return view.view_form()
    except Exception, e:
        logger.log_tracemsg("Invalid view request: %s" % e)
        
    raise http.Http404


@staff_member_required
def submit_form(request):
    """
    Edit worlddata.

    Args:
        request:

    Returns:
        None.
    """
    try:
        view = get_view(request)

        if "_back" in request.POST:
            return view.quit_form()
        elif "_delete" in request.POST:
            if view.is_valid():
                return view.delete_form()
        else:
            if view.is_valid():
                return view.submit_form()
    except Exception, e:
        logger.log_tracemsg("Invalid edit request: %s" % e)
        
    raise http.Http404


@staff_member_required
def add_form(request):
    """
    Edit worlddata.

    Args:
        request:

    Returns:
        None.
    """
    try:
        view = get_view(request)
        if view.is_valid():
            return view.add_form()
    except Exception, e:
        logger.log_tracemsg("Invalid edit request: %s" % e)

    raise http.Http404


@staff_member_required
def get_view(request):
    """
    Get form view's object.

    Args:
        request: Http request.
    Returns:
        view
    """
    try:
        path_list = request.path.split("/")
        form_name = path_list[-2]
    except Exception, e:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    relative_forms = {
        "world_exits": {"CLASS_LOCKED_EXIT": "exit_locks"},
        "world_objects": {"CLASS_OBJECT_CREATOR": "object_creators"}
    }

    if form_name in relative_forms:
        view = RelativeView(form_name, request, relative_forms[form_name])
    elif form_name == "game_settings" or form_name == "client_settings":
        view = SingleFormView(form_name, request)
    elif form_name == "dialogues":
        view = DialogueView(form_name, request)
    elif form_name == "dialogue_sentences":
        view = DialogueSentenceView(form_name, request)
    elif form_name == "dialogue_relations":
        view = DialogueChainView(form_name, request)
    else:
        view = FormView(form_name, request)

    return view


@staff_member_required
def get_image(request):
    """
    Create an image.

    Args:
        request:

    Returns:

    """
    try:
        image_view = get_image_view(request)
        if image_view.is_valid():
            return image_view.render()
    except Exception, e:
        logger.log_tracemsg("Invalid image request: %s" % e)

    raise http.Http404


@staff_member_required
def get_image_view(request):
    """
    Get image's render.

    Args:
        request: Http request.
    Returns:
        view
    """
    try:
        path_list = request.path.split("/")
        form_name = path_list[-2]
    except Exception, e:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    if form_name == "dialogue_relations":
        return DialogueChainImage(form_name, request)

    raise http.Http404