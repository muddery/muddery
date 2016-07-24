
"""
This file checks user's edit actions and put changes into db.
"""

import re
from django import http
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from worlddata import forms


def view_form(request):
    """
    Show a form of a record.

    Args:
        request: http request

    Returns:
        HttpResponse
    """
    # Get form's name form the request.
    request_data = request.GET

    try:
        path_list = request.path.split("/")
        form_name = path_list[-2]
    except Exception, e:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    try:
        form_class = forms.Manager.get_form(form_name)
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = request_data.get("_record", None)

    # Query data.
    model = form_class.Meta.model
    data = None
    if record:
        item = model.objects.get(pk=record)
        data = form_class(instance=item)
    else:
        data = form_class()

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = getattr(form_class.Meta, "form_template", settings.DEFUALT_FORM_TEMPLATE)

    context = {"form": form_name,
               "record": record,
               "data": data,
               "title": model._meta.verbose_name_plural,
               "desc": getattr(form_class.Meta, "desc", model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    return render(request, template_file, context)


def submit_form(request):
    """
    Edit or add a form of a record.

    Args:
        request: http request

    Returns:
        HttpResponse
    """
    request_data = request.POST

    # Get form's name form the request.
    try:
        path_list = request.path.split("/")
        form_name = path_list[-2]
    except Exception, e:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    try:
        form_class = forms.Manager.get_form(form_name)
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = request_data.get("_record", None)

    # Save data.
    data = None
    if record:
        item = form_class.Meta.model.objects.get(pk=record) 
        data = form_class(request_data, instance=item)
    else:
        data = form_class(request_data)

    if data.is_valid():
        data.save()

        if "_save" in request_data:
            # save and back
            return quit_form(request)

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = getattr(form_class.Meta, "form_template", settings.DEFUALT_FORM_TEMPLATE)

    context = {"form": form_name,
               "record": record,
               "data": data,
               "title": model._meta.verbose_name_plural,
               "desc": getattr(form_class.Meta, "desc", ""),
               "can_delete": (record is not None)}

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    return render(request, template_file, context)


def quit_form(request):
    """
    Quit a form without saving.
    Args:
        request: http request

    Returns:
        HttpResponse
    """
    request_data = request.POST

    if "_referrer" in request_data:
        referrer = request_data.get("_referrer")
        if referrer:
          return HttpResponseRedirect(referrer)

    try:
        pos = request.path.rfind("/")
        if pos > 0:
            url = request.path[:pos] + "/list.html"
            if "_page" in request_data:
                page = request_data.get("_page")
                url += "?_page=" + str(page)
            return HttpResponseRedirect(url)
    except Exception, e:
        logger.log_tracemsg("quit form error: %s" % e)

    raise http.Http404


def delete_form(request):
    """
    Delete a record.

    Args:
        request: http request

    Returns:
        HttpResponse
    """

    # Get form's name form the request.
    request_data = request.POST

    try:
        path_list = request.path.split("/")
        form_name = path_list[-2]
    except Exception, e:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    try:
        form_class = forms.Manager.get_form(form_name)
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    # Delete data.
    try:
        record = request_data.get("_record")
        item = model.objects.get(pk=record)
        item.delete()
    except Exception, e:
        raise MudderyError("Invalid record.")

    return quit_form(request)