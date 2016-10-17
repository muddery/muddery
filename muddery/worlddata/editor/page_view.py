
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
from worlddata import forms, models


def view_list(request):
    """
    Show a list of records.

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

    # Get models and recoreds.
    try:
        form_class = forms.Manager.get_form(form_name)
        model = form_class.Meta.model
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    fields = model._meta.get_fields()
    fields = [field for field in fields if not isinstance(field, ManyToOneRel)]
    records = model.objects.all()

    # Get template file's name form the request.
    template_file = settings.DEFUALT_LIST_TEMPLATE
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        try:
            template_file = form_class.Meta.list_template
        except:
            pass

    # Get page size and page number.
    page_size = 20
    page_number = request_data.get("_page", 1)

    # Divide pages.
    paginator = Paginator(records, page_size)
    try:
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage, InvalidPage):
        page = paginator.page(1)

    # Set range.
    page_range = 3

    range_begin = page.number - page_range
    if range_begin < 1:
        range_begin = 1

    range_end = page.number + page_range
    if range_end > paginator.num_pages:
        range_end = paginator.num_pages

    titles = [field.verbose_name for field in fields]
    page_records = [{"pk": record.pk, "items": [getattr(record, field.name) for field in fields]} for record in page]
    
    context = {"form": form_name,
               "titles": titles,
               "records": page_records,
               "page": page,
               "page_range": xrange(range_begin, range_end + 1),
               "self": request.get_full_path(),
               "title": model._meta.verbose_name_plural,
               "desc": getattr(form_class.Meta, "desc", model._meta.verbose_name_plural),}

    return render(request, template_file, context)


def quit_list(request):
    """
    Quit a list.

    "editor/category/form/list.html" => "editor/category.html"

    Args:
        request: http request

    Returns:
        HttpResponse
    """
    try:
        pos = request.path.rfind("/")
        pos = request.path.rfind("/", 0, pos)
        if pos > 0:
            url = request.path[:pos] + ".html"
            return HttpResponseRedirect(url)
    except Exception, e:
        logger.log_tracemsg("quit list error: %s" % e)

    raise http.Http404
