
"""
This file checks user's edit actions and put changes into db.
"""

import re
from django import http
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.db.models.fields.related import ManyToOneRel
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
    key = ""
    if record:
        instance = model.objects.get(pk=record)
        key = instance.key
        data = form_class(instance=instance)
    else:
        data = form_class()

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = "dialogue_form.html"

    # Dialogue sentences
    # Get models and recoreds.
    try:
        form_class = forms.Manager.get_form("dialogue_sentences")
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % "dialogue_sentences")

    fields = model._meta.get_fields()
    fields = [field for field in fields if not isinstance(field, ManyToOneRel)]
    sentences = model.objects.filter(dialogue=key)

    sentences = [{"pk": sentence.pk, "items": [getattr(sentence, field.name, "") for field in fields]} for sentence in sentences]

    context = {"form": form_name,
               "data": data,
               "key": key,
               "title": model._meta.verbose_name_plural,
               "desc": getattr(form_class.Meta, "desc", model._meta.verbose_name_plural),
               "can_delete": (record is not None),
               "fields": fields,
               "sentences": sentences,
               "self": request.get_full_path()}

    if record:
        context["record"] = record

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

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
    key = ""
    if record:
        instance = model.objects.get(pk=record)
        key = instance.key
        data = form_class(request_data, instance=instance)
    else:
        data = form_class(request_data)

    if data.is_valid():
        instance = data.save()
        record = instance.pk
        key = instance.key

        if "_save" in request_data:
            # save and back
            return quit_form(form_name, request)

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = "dialogue_form.html"

    # Dialogue sentences
    # Get models and recoreds.
    try:
        form_class = forms.Manager.get_form("dialogue_sentences")
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % "dialogue_sentences")

    fields = model._meta.get_fields()
    fields = [field for field in fields if not isinstance(field, ManyToOneRel)]
    sentences = model.objects.filter(dialogue=key)

    sentences = [{"pk": sentence.pk, "items": [getattr(sentence, field.name, "") for field in fields]} for sentence in sentences]

    context = {"form": form_name,
               "data": data,
               "key": key,
               "title": model._meta.verbose_name_plural,
               "desc": getattr(form_class.Meta, "desc", model._meta.verbose_name_plural),
               "can_delete": (record is not None),
               "fields": fields,
               "sentences": sentences,
               "self": request.get_full_path()}

    if record:
        context["record"] = record

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

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