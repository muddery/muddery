
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


def view(request):
    """
    Show a list of records.

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

    try:
        form_class = forms.Manager.get_form(form_name)
    except Exception, e:
        raise MudderyError("Invalid form: %s." % form_name)

    # Get models and recoreds.
    model = form_class.Meta.model
    fields = model._meta.get_fields()
    fields = [field for field in fields if not isinstance(field, ManyToOneRel)]
    records = model.objects.all()

    # Get template file's name form the request.
    template_file = settings.DEFUALT_LIST_TEMPLATE
    if "_template" in request_data:
        template_file = request_data.get("_template")
    else:
        try:
            template_file = form_class.Template.list_template
        except:
            pass

    referrer = request_data.get("_referrer", "")

    # Get page size and page number.
    page_size = request_data.get("_page_size", 20)
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

    page_records = [{"pk": record.pk, "items": [getattr(record, field.name, "") for field in fields]} for record in page]

    return render(request, template_file, {"form": form_name,
                                           "fields": fields,
                                           "records": page_records,
                                           "page": page,
                                           "page_range": xrange(range_begin, range_end + 1),
                                           "referrer": referrer,
                                           "title": model._meta.verbose_name_plural,
                                           "desc": model.__doc__})
        