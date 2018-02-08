
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
from muddery.worlddata.editor.page_view import PageView
from muddery.worlddata.data_sets import DATA_SETS
from worlddata import forms, models


class RoomListView(PageView):
    """
    This object deal with room's records list.
    """
    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        # Get form's class.
        try:
            self.form_class = forms.Manager.get_form(self.form_name)
        except Exception, e:
            logger.log_tracemsg("Invalid form %s: %s." % (self.form_name, e))
            self.error = "Invalid form: %s." % self.form_name
            return False

        # Get template file's name form the request.
        self.template_file = "room_list.html"
        return True

    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        try:
            path_list = self.request.path.split("/")
            form_name = path_list[-2]
        except Exception, e:
            logger.log_errmsg("Invalid form.")
            raise http.Http404

        # Get all areas.
        areas = []
        try:
            area_records = DATA_SETS.world_areas.objects.all()
            areas = [{"key": a.key, "name": a.name + "(" + a.key + ")"} for a in area_records]
            areas.append({"key": "", "name": "------------"})
        except:
            areas = []

        area = self.request_data.get("_area", None)
        if area is None and areas:
            area = areas[0]["key"]

        # Get models and recoreds.
        try:
            form_class = forms.Manager.get_form(form_name)
            model = form_class.Meta.model
        except Exception, e:
            raise MudderyError("Invalid form: %s." % form_name)

        fields = model._meta.get_fields()
        fields = [field for field in fields if not isinstance(field, ManyToOneRel)]
        
        if area:
            records = model.objects.filter(location=area)
        else:
            records = model.objects.all()

        # Get page size and page number.
        page_size = 5
        page_number = self.request_data.get("_page", 1)

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
                   "self": self.request.get_full_path(),
                   "title": model._meta.verbose_name_plural,
                   "desc": getattr(form_class.Meta, "desc", model._meta.verbose_name_plural),
                   "can_add": True,
                   "area": area,
                   "areas": areas}

        return context

    def view_list(self, request):
        """
        Show a list of records.

        Args:
            request: http request

        Returns:
            HttpResponse
        """
        context = self.get_context()
        return render(request, self.template_file, context)

    def quit_list(self, request):
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
