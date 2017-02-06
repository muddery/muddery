
"""
This file checks user's edit actions and put changes into db.
"""

from django import http
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from worlddata import forms


class FormView(object):
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
        self.form_name = form_name
        self.request = request

        # get request data
        if self.request.POST:
            self.request_data = self.request.POST
        else:
            self.request_data = self.request.GET

        self.files = self.request.FILES

        # initialize values
        self.valid = None
        self.form_class = None
        self.data = None
        self.page = None
        self.record = None
        self.key = None
        self.template_file = None
        self.error = None

    def is_valid(self):
        """
        Validate the request.

        Returns:
            boolean: is valid
        """
        if self.valid is None:
            # If the request has not been parsed, parse it.
            self.valid = self.parse_request()

        return self.valid

    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        # record's page and id
        self.page = self.request_data.get("_page", None)
        self.record = self.request_data.get("_record", None)

        # Get form's class.
        try:
            self.form_class = forms.Manager.get_form(self.form_name)
        except Exception, e:
            logger.log_tracemsg("Invalid form %s: %s." % (self.form_name, e))
            self.error = "Invalid form: %s." % self.form_name
            return False

        # Get template file's name.
        self.template_file = getattr(self.form_class.Meta, "form_template", settings.DEFUALT_FORM_TEMPLATE)

        return True

    def query_view_data(self):
        """
        Get db instance for view.

        Returns:
            None
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        self.data = None
        self.key = None
        if self.record:
            try:
                # Query record's data.
                instance = self.form_class.Meta.model.objects.get(pk=self.record)
                self.data = self.form_class(instance=instance)
                self.key = getattr(instance, "key", None)
            except Exception, e:
                self.data = None

        if not self.data:
            # Get empty data.
            self.data = self.form_class()

    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        # Query data.
        if not self.data:
            self.query_view_data()

        verbose_name = self.form_class.Meta.model._meta.verbose_name_plural
        context = {"data": self.data,
                   "title": verbose_name,
                   "desc": getattr(self.form_class.Meta, "desc", verbose_name),
                   "can_delete": (self.record is not None)}

        if self.record:
            context["record"] = self.record

        if self.page:
            context["page"] = self.page

        return context

    def view_form(self):
        """
        Show the edit form of a record.

        Returns:
            HttpResponse
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        context = self.get_context()

        return render(self.request, self.template_file, context)

    def query_submit_data(self):
        """
        Get db instance to submit a record.

        Returns:
            None
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        self.data = None
        self.key = None
        if self.record:
            try:
                # Query existing record's data.
                instance = self.form_class.Meta.model.objects.get(pk=self.record)
                self.data = self.form_class(self.request_data, self.files, instance=instance)
                self.key = getattr(instance, "key", None)
            except Exception, e:
                self.data = None

        if not self.data:
            # Create new data.
            self.data = self.form_class(self.request_data, self.files)

    def submit_form(self):
        """
        Edit a record.

        Returns:
            HttpResponse
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        # Query data.
        if not self.data:
            self.query_submit_data()

        # Save data
        if self.data.is_valid():
            instance = self.data.save()
            self.record = instance.pk

            try:
                self.key = instance.key
            except Exception, e:
                pass

            if "_save" in self.request_data:
                # Save and quit.
                return self.quit_form()

        # Save and continue editing.
        return self.view_form()

    def add_form(self):
        """
        Add a record.

        Returns:
            HttpResponse
        """
        return self.view_form()

    def quit_form(self):
        """
        Quit a form without saving.

        Returns:
            HttpResponse
        """
        try:
            # Back to record list.
            # Parse list's url from the request path.
            pos = self.request.path.rfind("/")
            if pos > 0:
                url = self.request.path[:pos] + "/list.html"
                if self.page:
                    url += "?_page=" + str(self.page)
                return HttpResponseRedirect(url)
        except Exception, e:
            logger.log_tracemsg("Quit form error: %s" % e)

        raise http.Http404

    def delete_form(self):
        """
        Delete a record.

        Returns:
            HttpResponse
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        # Delete record.
        if self.record:
            try:
                instance = self.form_class.Meta.model.objects.get(pk=self.record)
                instance.delete()
            except Exception, e:
                pass

        return self.quit_form()
