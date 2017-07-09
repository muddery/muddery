
"""
This file checks user's edit actions and put changes into db.
"""

from muddery.worlddata.editor.page_view import PageView


class FixedPageView(PageView):
    """
    Users can not add new records to FixedPageView.
    """
    def get_context(self):
        """
        Show a list of records.

        Args:
            request: http request

        Returns:
            HttpResponse
        """
        context = super(FixedPageView, self).get_context()
        context["can_add"] = False
        return context