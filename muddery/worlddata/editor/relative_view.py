
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


def view_form(request, base_form_name, default_template, relative_forms):
    """
    Show a form of a record.

    Args:
        request: http request
        relative_forms: dict {relative_typeclass: relative_form_name}

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

    record = request_data.get("_record", None)

    # Query data.
    if record:
        base_instance = base_model.objects.get(pk=record)
        base_data = base_class(instance=base_instance)
    else:
        base_data = base_class()

    relative_data = []
    relative_typeclasses = list(relative_forms)
    for typeclass, form_name in relative_forms.iteritems():
        try:
            relative_class = forms.Manager.get_form(form_name)
            relative_model = relative_class.Meta.model
        except Exception, e:
            raise MudderyError("Invalid form: %s." % form_name)

        # relativeal data
        data = relative_class()
        if record:
            try:
                relative_instance = relative_model.objects.get(key=base_instance.key)
                data = relative_class(instance=relative_instance)
            except Exception, e:
                pass
        relative_data.append({"typeclass": typeclass, "data": data})

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = default_template

    context = {"form": base_form_name,
               "base_data": base_data,
               "relative_data": relative_data,
               "relative_typeclasses": relative_typeclasses,
               "title": base_model._meta.verbose_name_plural,
               "desc": getattr(base_class.Meta, "desc", base_model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if record:
        context["record"] = record

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

    return render(request, template_file, context)


def submit_form(request, base_form_name, default_template, relative_forms):
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

    record = request_data.get("_record", None)

    # make base data.
    base_data = base_class(request_data)
    base_instance = None

    if record:
        base_instance = base_model.objects.get(pk=record)
        base_data = base_class(request_data, instance=base_instance)

    # make relative data
    relative_data = {}
    relative_typeclasses = list(relative_forms)
    for typeclass, form_name in relative_forms.iteritems():
        try:
            relative_class = forms.Manager.get_form(form_name)
            relative_model = relative_class.Meta.model
        except Exception, e:
            raise MudderyError("Invalid form: %s." % form_name)

        # relativeal data
        data = relative_class(request_data)
        if record:
            try:
                relative_instance = relative_model.objects.get(key=base_instance.key)
                data = relative_class(request_data, instance=relative_instance)
            except Exception, e:
                pass

        relative_data[typeclass] = data

    # Validate
    saved = False
    typeclass = request_data["typeclass"]
    if typeclass not in relative_data:
        if base_data.is_valid():
            with transaction.atomic():
                base_data.save()
                # Keep old lock data, comment following codes.
                # if lock_instance:
                #     lock_instance.delete()
                saved = True
    else:
        # Prevent short cut.
        base_valid = base_data.is_valid()
        relative_valid = relative_data[typeclass].is_valid()

        if base_valid and relative_valid:
            with transaction.atomic():
                base_data.save()
                relative_data[typeclass].save()
                saved = True

    if saved and "_save" in request_data:
        # save and back
        return quit_form(request)

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = default_template

    context = {"form": base_form_name,
               "base_data": base_data,
               "relative_data": [({"typeclass": key, "data": relative_data[key]}) for key in relative_data],
               "relative_typeclasses": relative_typeclasses,
               "title": base_model._meta.verbose_name_plural,
               "desc": getattr(base_class.Meta, "desc", base_model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if record:
        context["record"] = record

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


def delete_form(request, base_form_name, relative_forms):
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

    # Delete data.
    try:
        record = request_data.get("_record")
        item = base_model.objects.get(pk=record)
        key = item.key
        item.delete()
    except Exception, e:
        raise MudderyError("Invalid record.")

    for typeclass, form_name in relative_forms.iteritems():
        try:
            relative_class = forms.Manager.get_form(form_name)
            relative_model = relative_class.Meta.model
        except Exception, e:
            raise MudderyError("Invalid form: %s." % form_name)

        # Delete data.
        try:
            item = relative_model.objects.get(key=key)
            item.delete()
        except Exception, e:
            pass

    return quit_form(request)