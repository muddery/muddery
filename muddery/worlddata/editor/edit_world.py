
"""
This file checks user's edit actions and put changes into db.
"""

import re
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect  
from muddery.utils.exception import MudderyError
from worlddata import forms


def view_form(request):
    """
    Show a new form.

    Args:
        form_name: the name of a form

    Returns:
        web page
    """
    form_name = None
    if "_form" in request.GET:
        form_name = request.GET.get("_form")
    else:
        logger.log_tracemsg("Invalid form.")
        raise http.Http404

    form_class = None
    try:
        form_class = forms.Manager.get_form(form_name)
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = None
    if "_record" in request.GET:
        record = request.GET.get("_record")

    form_data = None
    if record:
        item = form_class.Meta.model.objects.get(pk=record) 
        form_data = form_class(instance=item) 
    else:
        form_data = form_class()

    page_name = re.sub(r"^/admin/worlddata/editor/", "", request.path)
    page_name = re.sub(r"form.html$", "", page_name) + form_name + ".html"
    return render(request, page_name, {'form': form_data})


def submit_form(request):
    """
    Args:
        data: User action's data.

    Returns:
        None.
    """
    if "_quit" in request.POST:
        if "_referrer" in request.POST:
            referrer = request.POST.get("_referrer")
            return HttpResponseRedirect(referrer)
        else:
            return HttpResponseRedirect("./index.html")

    form_name = None
    if "_form" in request.POST:
        form_name = request.POST.get("_form")
    else:
        logger.log_tracemsg("Invalid form.")
        raise http.Http404

    form_class = None
    try:
        form_class = forms.Manager.get_form(form_name)
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    record = None
    if "_record" in request.POST:
        record = request.POST.get("_record")

    form_data = None
    if record:
        item = form_class.Meta.model.objects.get(pk=record) 
        form_data = form_class(request.POST, instance=item) 
    else:
        form_data = form_class(request.POST)

    if form_data.is_valid():
        form_data.save()

        if "_save" in request.POST:
            if "_referrer" in request.POST:
                referrer = request.POST.get("_referrer")
                return HttpResponseRedirect(referrer)
            else:
                return HttpResponseRedirect("./index.html")
       
    page_name = re.sub(r"^/admin/worlddata/editor/", "", request.path)
    page_name = re.sub(r"submit.html$", "", page_name) + form_name + ".html"
    return render(request, page_name, {'form': form_data})
