
"""
This file checks user's edit actions and put changes into db.
"""

import re
from django import http
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from django.db import transaction
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from worlddata import forms


def view_form(base_form_name, addition_form_name, default_template, addition_typeclass, request):
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
        base_class = forms.Manager.get_form(base_form_name)
        base_model = base_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % base_form_name)

    try:
        addition_class = forms.Manager.get_form(addition_form_name)
        addition_model = addition_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % addition_form_name)

    record = request_data.get("_record", None)

    # Query data.
    if record:
        base_instance = base_model.objects.get(pk=record)
        base = base_class(instance=base_instance)
    else:
        base = base_class()
        
    # additional data
    addition = addition_class()
    if record:
        try:
            addition_instance = addition_model.objects.get(key=base_instance.key)
            addition = addition_class(instance=addition_instance)
        except Exception, e:
            pass

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = default_template

    context = {"form": base_form_name,
               "record": record,
               "base": base,
               "addition": addition,
               "addition_typeclass": addition_typeclass,
               "title": base_model._meta.verbose_name_plural,
               "desc": getattr(base_class.Meta, "desc", base_model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

    return render(request, template_file, context)


def submit_form(base_form_name, addition_form_name, default_template, addition_typeclass, request):
    """
    Edit or add a form of a record.

    Args:
        request: http request

    Returns:
        HttpResponse
    """
    request_data = request.POST

    try:
        base_class = forms.Manager.get_form(base_form_name)
        base_model = base_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % base_form_name)

    try:
        addition_class = forms.Manager.get_form(addition_form_name)
        addition_model = addition_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % addition_form_name)

    record = request_data.get("_record", None)

    # Save data.
    base = base_class(request_data)
    addition = addition_class(request_data)
    
    base_instance = None
    addition_instance = None
    
    if record:
        base_instance = base_model.objects.get(pk=record)
        base = base_class(request_data, instance=base_instance)

        try:
            addition_instance = addition_model.objects.get(key=base_instance.key)
            addition = addition_class(request_data, instance=addition_instance)
        except Exception, e:
            pass

    # Validate
    saved = False
    if request_data["typeclass"] != addition_typeclass:
        if base.is_valid():
            with transaction.atomic():
                base.save()
                # Keep old lock data, comment following codes.
                # if lock_instance:
                #     lock_instance.delete()
                saved = True
    else:
        # Prevent short cut.
        base_valid = base.is_valid()
        addition_valid = addition.is_valid()

        if base_valid and addition_valid:
            with transaction.atomic():
                base.save()
                addition.save()
                saved = True

    if saved and "_save" in request_data:
        # save and back
        return quit_form(base_form_name, request)

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = default_template

    context = {"form": base_form_name,
               "record": record,
               "base": base,
               "addition": addition,
               "addition_typeclass": addition_typeclass,
               "title": base_model._meta.verbose_name_plural,
               "desc": getattr(base_class.Meta, "desc", base_model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

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


def delete_form(base_form_name, addition_form_name, request):
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
        base_class = forms.Manager.get_form(base_form_name)
        base_model = base_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % base_form_name)

    try:
        addition_class = forms.Manager.get_form(addition_form_name)
        addition_model = addition_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % addition_form_name)

    # Delete data.
    try:
        record = request_data.get("_record")

        item = base_model.objects.get(pk=record)
        item.delete()

        try:
            item = addition_model.objects.get(pk=record)
            item.delete()
        except Exception, e:
            pass

    except Exception, e:
        raise MudderyError("Invalid record.")

    return quit_form(request)