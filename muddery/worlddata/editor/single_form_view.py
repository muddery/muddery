
"""
This file checks user's edit actions and put changes into db.
"""

from django import http
from django.shortcuts import render
from django.http import HttpResponseRedirect
from evennia.utils import logger
from muddery.worlddata.editor.form_view import FormView
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
