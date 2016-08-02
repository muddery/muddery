
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


def view_form(exit_form_name, request):
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
        exit_class = forms.Manager.get_form(exit_form_name)
        exit_model = exit_class.Meta.model
        
        lock_class = forms.Manager.get_form("exit_locks")
        lock_model = lock_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % exit_form_name)

    record = request_data.get("_record", None)

    # Query data.
    if record:
        item = exit_model.objects.get(pk=record)
        exit = exit_class(instance=item)
    else:
        exit = exit_class()
        
    # Lock data
    lock = lock_class()
    if record:
        try:
            item = lock_model.objects.get(pk=record)
            lock = lock_class(instance=item)
        except Exception, e:
            pass

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = "exits.html"

    context = {"form": exit_form_name,
               "record": record,
               "exit": exit,
               "lock": lock,
               "title": exit_model._meta.verbose_name_plural,
               "desc": getattr(exit_class.Meta, "desc", exit_model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

    return render(request, template_file, context)


def submit_form(exit_form_name, request):
    """
    Edit or add a form of a record.

    Args:
        request: http request

    Returns:
        HttpResponse
    """
    request_data = request.POST

    try:
        exit_class = forms.Manager.get_form(exit_form_name)
        exit_model = exit_class.Meta.model
        
        lock_class = forms.Manager.get_form("exit_locks")
        lock_model = lock_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % exit_form_name)

    record = request_data.get("_record", None)

    # Save data.
    if record:
        item = exit_model.objects.get(pk=record) 
        exit = exit_class(request_data, instance=item)
    else:
        exit = exit_class(request_data)

    lock = lock_class(request_data)

    if exit.is_valid():
        if request_data["typeclass"] != "CLASS_LOCKED_EXIT":
            exit.save()

            # If it is not a locked exit, remove its lock records.
            try:
                lock = lock_model.objects.get(pk=record)
                lock.delete()
            except Exception, e:
                pass
        
            if "_save" in request_data:
                # save and back
                return quit_form(exit_form_name, request)
        else:
            # Check lock's data.
            if record:
                try:
                    item = lock_model.objects.get(pk=record)
                    lock = lock_class(request_data, instance=item)
                except Exception, e:
                    pass

            if lock.is_valid():
                exit.save()
                lock.save()

                if "_save" in request_data:
                    # save and back
                    return quit_form(exit_form_name, request)

    # Get template file's name form the request.
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        template_file = "exits.html"

    context = {"form": exit_form_name,
               "record": record,
               "exit": exit,
               "lock": lock,
               "title": exit_model._meta.verbose_name_plural,
               "desc": getattr(exit_class.Meta, "desc", exit_model._meta.verbose_name_plural),
               "can_delete": (record is not None)}

    if "_page" in request_data:
        context["page"] = request_data.get("_page")

    if "_referrer" in request_data:
        context["referrer"] = request_data.get("_referrer")

    return render(request, template_file, context)


def quit_form(exit_form_name, request):
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


def delete_form(exit_form_name, request):
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
        exit_class = forms.Manager.get_form(exit_form_name)
        exit_model = exit_class.Meta.model
        
        lock_class = forms.Manager.get_form("exit_locks")
        lock_model = lock_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % exit_form_name)

    # Delete data.
    try:
        record = request_data.get("_record")

        item = exit_model.objects.get(pk=record)
        item.delete()

        try:
            item = lock_model.objects.get(pk=record)
            item.delete()
        except Exception, e:
            pass

    except Exception, e:
        raise MudderyError("Invalid record.")

    return quit_form(request)