
"""
This file checks user's edit actions and put changes into db.
"""

from django.http import HttpResponseRedirect
from muddery.worlddata.editor.form_view import FormView
from worlddata import forms


class DialogueSentenceView(FormView):
    """
    This object deal with dialogue_sentence's edit forms and views.
    """

    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        if not super(DialogueSentenceView, self).parse_request():
            return False

        self.template_file = getattr(self.form_class.Meta, "form_template", "dialogue_sentence_form.html")
        return True

    def query_view_data(self):
        """
        Get db instance for view.

        Returns:
            None
        """
        super(DialogueSentenceView, self).query_view_data()

        if self.data:
            # Can not change the relative dialogue.
            # self.data.fields["dialogue"].disabled = True
            self.data.fields["dialogue"].initial = self.request_data["_dialogue_key"]

    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        context = super(DialogueSentenceView, self).get_context()

        if "_back_page" in self.request_data:
            context["back_page"] = self.request_data.get("_back_page")

        if "_back_record" in self.request_data:
            context["back_record"] = self.request_data.get("_back_record")

        if "_dialogue_key" in self.request_data:
            context["dialogue_key"] = self.request_data.get("_dialogue_key")

        return context

    def query_submit_data(self):
        """
        Get db instance to submit a record.

        Returns:
            None
        """
        super(DialogueSentenceView, self).query_submit_data()

        if self.data:
            # Can not change the relative dialogue.
            # self.data.fields["dialogue"].disabled = True
            self.data.fields["dialogue"].initial = self.request_data["_dialogue_key"]

    def quit_form(self):
        """
        Quit a form without saving.

        Returns:
            HttpResponse
        """
        # Back to the dialogue's form.
        url = "dialogues/dialogues/form.html"
        if ("_back_page" in self.request_data) and ("_back_record" in self.request_data):
            url += "?_page=" + self.request_data["_back_page"] + "&_record=" + self.request_data["_back_record"]

        return HttpResponseRedirect(url)
