
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
    form_name = None
    if "_form" in request_data:
        form_name = request_data.get("_form")
    else:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    form_class = None
    try:
        form_class = forms.Manager.get_form(form_name)
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

    referrer = request_data.get("_referrer", "")

    # Get template file's name form the request.
    template_file = settings.DEFUALT_FORM_TEMPLATE
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        try:
            template_file = form_class.Template.form_template
        except:
            pass

    return render(request, template_file, {"form": form_name,
                                           "record": record,
                                           "data": data,
                                           "referrer": referrer,
                                           "title": model._meta.verbose_name_plural,
                                           "desc": model.__doc__,
                                           "can_delete": (record is not None)})


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
    form_name = None
    if "_form" in request_data:
        form_name = request_data.get("_form")
    else:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    form_class = None
    try:
        form_class = forms.Manager.get_form(form_name)
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = request_data.get("_record", None)

    # Save data.
    model = form_class.Meta.model
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
            if "_referrer" in request_data:
                referrer = request_data.get("_referrer")
                if referrer:
                    return HttpResponseRedirect(referrer)

            return HttpResponseRedirect("./index.html")

    # Get template file's name form the request.
    template_file = settings.DEFUALT_FORM_TEMPLATE
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        try:
            template_file = form_class.Template.form_template
        except:
            pass

    return render(request, template_file, {"form": form_name,
                                           "record": record,
                                           "data": data,
                                           "title": model._meta.verbose_name_plural,
                                           "desc": model.__doc__,
                                           "can_delete": (record is not None)})


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

    return HttpResponseRedirect("./index.html")


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

    form_name = None
    if "_form" in request_data:
        form_name = request_data.get("_form")
    else:
        logger.log_errmsg("Invalid form.")
        raise http.Http404

    form_class = None
    try:
        form_class = forms.Manager.get_form(form_name)
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = request_data.get("_record", None)

    # Delete data.
    if record:
        item = form_class.Meta.model.objects.get(pk=record)
        item.delete()
    else:
        raise MudderyError("Invalid record: %s." % record)

    if "_referrer" in request_data:
        referrer = request_data.get("_referrer")
        if referrer:
            return HttpResponseRedirect(referrer)

    return HttpResponseRedirect("./index.html")