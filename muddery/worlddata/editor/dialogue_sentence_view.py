
"""
This file checks user's edit actions and put changes into db.
"""

import re
import json
from django import http
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from worlddata import forms


def view_form(form_name, request):
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
        form_class = forms.Manager.get_form(form_name)
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = request_data.get("_record", None)

    # Query data.
    if record:
        item = model.objects.get(pk=record)
        data = form_class(instance=item)
    else:
        data = form_class()

    data.fields["dialogue"].disabled = True
    data.fields["dialogue"].initial = request_data["_dialogue"]

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = "dialogue_sentence_form.html"

    context = {"form": form_name,
               "data": data,
               "dialogue": request_data["_dialogue"],
               "title": model._meta.verbose_name_plural,
               "desc": getattr(form_class.Meta, "desc", model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if record:
        context["record"] = record
        
    if "_back_page" in request_data:
        context["back_page"] = request_data.get("_back_page")

    if "_back_record" in request_data:
        context["back_record"] = request_data.get("_back_record")

    return render(request, template_file, context)


def submit_form(form_name, request):
    """
    Edit or add a form of a record.

    Args:
        request: http request

    Returns:
        HttpResponse
    """
    request_data = request.POST

    try:
        form_class = forms.Manager.get_form(form_name)
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = request_data.get("_record", None)

    # Save data.
    if record:
        item = model.objects.get(pk=record) 
        data = form_class(request_data, instance=item)
    else:
        data = form_class(request_data)

    data.fields["dialogue"].disabled = True
    data.fields["dialogue"].initial = request_data["_dialogue"]

    if data.is_valid():
        item = data.save()
        record = item.pk

        if "_save" in request_data:
            # save and back
            return quit_form(form_name, request)

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = "dialogue_sentence_form.html"

    context = {"form": form_name,
               "data": data,
               "dialogue": request_data["_dialogue"],
               "title": model._meta.verbose_name_plural,
               "desc": getattr(form_class.Meta, "desc", model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if record:
        context["record"] = record

    if "_back_page" in request_data:
        context["back_page"] = request_data.get("_back_page")

    if "_back_record" in request_data:
        context["back_record"] = request_data.get("_back_record")

    return render(request, template_file, context)


def quit_form(form_name, request):
    """
    Quit a form without saving.
    Args:
        request: http request

    Returns:
        HttpResponse
    """
    request_data = request.POST

    url = "dialogues/dialogues/form.html"
    if ("_back_page" in request_data) and ("_back_record" in request_data):
        url += "?_page=" + request_data["_back_page"] + "&_record=" + request_data["_back_record"]

    return HttpResponseRedirect(url)


def delete_form(form_name, request):
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

    return quit_form(form_name, request)