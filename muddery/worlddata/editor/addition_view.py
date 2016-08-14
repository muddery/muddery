
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


def view_form(request, base_form_name, default_template, addition_forms):
    """
    Show a form of a record.

    Args:
        request: http request
        addition_forms: dict {addition_typeclass: addition_form_name}

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

    addition_data = []
    addition_typeclasses = list(addition_forms)
    for typeclass, form_name in addition_forms.iteritems():
        try:
            addition_class = forms.Manager.get_form(form_name)
            addition_model = addition_class.Meta.model
        except Exception, e:
            raise MudderyError("Invalid form: %s." % form_name)

        # additional data
        data = addition_class()
        if record:
            try:
                addition_instance = addition_model.objects.get(key=base_instance.key)
                data = addition_class(instance=addition_instance)
            except Exception, e:
                pass
        addition_data.append({"typeclass": typeclass, "data": data})

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = default_template

    context = {"form": base_form_name,
               "record": record,
               "base_data": base_data,
               "addition_data": addition_data,
               "addition_typeclasses": addition_typeclasses,
               "title": base_model._meta.verbose_name_plural,
               "desc": getattr(base_class.Meta, "desc", base_model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

    return render(request, template_file, context)


def submit_form(request, base_form_name, default_template, addition_forms):
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

    # make addition data
    addition_data = {}
    addition_typeclasses = list(addition_forms)
    for typeclass, form_name in addition_forms.iteritems():
        try:
            addition_class = forms.Manager.get_form(form_name)
            addition_model = addition_class.Meta.model
        except Exception, e:
            raise MudderyError("Invalid form: %s." % form_name)

        # additional data
        data = addition_class(request_data)
        if record:
            try:
                addition_instance = addition_model.objects.get(key=base_instance.key)
                data = addition_class(request_data, instance=addition_instance)
            except Exception, e:
                pass

        addition_data[typeclass] = data

    # Validate
    saved = False
    typeclass = request_data["typeclass"]
    if typeclass not in addition_data:
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
        addition_valid = addition_data[typeclass].is_valid()

        if base_valid and addition_valid:
            with transaction.atomic():
                base_data.save()
                addition_data[typeclass].save()
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
               "record": record,
               "base_data": base_data,
               "addition_data": [({"typeclass": key, "data": addition_data[key]}) for key in addition_data],
               "addition_typeclasses": addition_typeclasses,
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