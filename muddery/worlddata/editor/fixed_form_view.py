
"""
This file checks user's edit actions and put changes into db.
"""

from django import http
from muddery.worlddata.editor.form_view import FormView


class FixedFormView(FormView):
    """
    Users can not delete records from FixedPageView.
    """
    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        context = super(FixedFormView, self).get_context()
        context["can_delete"] = False

        return context

    def add_form(self):
        """
        Can not add.

        Returns:
            HttpResponse
        """
        raise http.Http404

    def delete_form(self):
        """
        Can not delete.

        Returns:
            HttpResponse
        """
        raise http.Http404
