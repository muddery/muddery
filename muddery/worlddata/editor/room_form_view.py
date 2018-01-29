
"""
This file checks user's edit actions and put changes into db.
"""

from django import http
from django.http import HttpResponseRedirect
from evennia.utils import logger
from muddery.worlddata.editor.form_view import FormView
from worlddata import forms


class RoomFormView(FormView):
    """
    This object deal with common forms and views.
    """
    def __init__(self, form_name, request):
        """
        Set form name and request.

        Args:
            form_name: model form's name
            request: http request

        Returns:
            None
        """
        super(RoomFormView, self).__init__(form_name, request)
        self.area = None

    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        # record's page and id
        self.page = self.request_data.get("_page", None)
        self.record = self.request_data.get("_record", None)
        self.area = self.request_data.get("_area", None)

        # Get form's class.
        try:
            self.form_class = forms.Manager.get_form(self.form_name)
        except Exception, e:
            logger.log_tracemsg("Invalid form %s: %s." % (self.form_name, e))
            self.error = "Invalid form: %s." % self.form_name
            return False

        # Get template file's name.
        self.template_file = "room_form.html"

        return True

    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        context = super(RoomFormView, self).get_context()
        if self.area:
            context["area"] = self.area

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
                if self.area:
                    if args:
                        args += "&"
                    args += "_area=" + self.area

                if args:
                    url += "?" + args

                return HttpResponseRedirect(url)
        except Exception, e:
            logger.log_tracemsg("Quit form error: %s" % e)

        raise http.Http404
