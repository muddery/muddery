
"""
This file checks user's edit actions and put changes into db.
"""

from django import http
from django.shortcuts import render
from django.http import HttpResponseRedirect
from evennia.utils import logger
from muddery.worlddata.editor.form_view import FormView
from muddery.utils.exception import MudderyError
from worlddata import forms


class SingleFormView(FormView):
    """
    This object deal with the basic define record forms and views.
    """
    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        context = super(SingleFormView, self).get_context()
        context["can_delete"] = False

        return context

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

        try:
            # Query the only data.
            instance = self.form_class.Meta.model.objects.get()
            self.data = self.form_class(instance=instance)
            self.key = getattr(instance, "key", None)
        except Exception, e:
            self.data = None

        if not self.data:
            # Get empty data.
            self.data = self.form_class()

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

        try:
            # Query the only data.
            instance = self.form_class.Meta.model.objects.get()
            self.data = self.form_class(self.request_data, instance=instance)
            self.key = getattr(instance, "key", None)
        except Exception, e:
            self.data = None

        if not self.data:
            # Create new data.
            self.data = self.form_class(self.request_data)

    def add_form(self):
        """
        Can not add a single form.

        Returns:
            HttpResponse
        """
        raise http.Http404

    def quit_form(self):
        """
        Quit a form without saving.

        Returns:
            HttpResponse
        """
        try:
            pos = self.request.path.rfind("/")
            pos = self.request.path.rfind("/", 0, pos)
            if pos > 0:
                url = self.request.path[:pos] + ".html"
                return HttpResponseRedirect(url)
        except Exception, e:
            logger.log_tracemsg("quit list error: %s" % e)

        raise http.Http404

    def delete_form(self):
        """
        Can not delete a single form.

        Returns:
            HttpResponse
        """
        raise http.Http404
