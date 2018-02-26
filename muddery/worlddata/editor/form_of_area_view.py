
"""
This file checks user's edit actions and put changes into db.
"""

from django import http
from django.http import HttpResponseRedirect
from evennia.utils import logger
from muddery.worlddata.editor.form_view import FormView
from muddery.worlddata.data_sets import DATA_SETS
from worlddata import forms


class FormOfAreaView(FormView):
    """
    This object deal with common forms and views.
    """
    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        result = super(FormOfAreaView, self).parse_request()

        # Get template file's name.
        self.template_file = "form_of_area.html"

        return result

    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        context = super(FormOfAreaView, self).get_context()

        area = None
        try:
            room_key = self.request_data.get("location")
            room = DATA_SETS.world_rooms.objects.get(key=room_key)
            area = room.location
        except Exception, e:
            area = self.request_data.get("_area", None)
        if area:
            context["area"] = area

        return context

    def quit_form(self):
        """
        Quit a form without saving.

        Returns:
            HttpResponse
        """
        self.parse_request()

        try:
            # Back to record list.
            # Parse list's url from the request path.
            pos = self.request.path.rfind("/")
            if pos > 0:
                url = self.request.path[:pos] + "/list.html"

                args = ""
                if self.page:
                    args += "_page=" + str(self.page)

                area = None
                try:
                    room_key = self.request_data.get("location")
                    room = DATA_SETS.world_rooms.objects.get(key=room_key)
                    area = room.location
                except Exception, e:
                    area = self.request_data.get("_area", None)

                if area:
                    if args:
                        args += "&"
                    args += "_area=" + area

                if args:
                    url += "?" + args

                return HttpResponseRedirect(url)
        except Exception, e:
            logger.log_tracemsg("Quit form error: %s" % e)

        raise http.Http404
