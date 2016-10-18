
"""
This file checks user's edit actions and put changes into db.
"""

from django.db import transaction
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.worlddata.editor.form_view import FormView
from worlddata import forms


class RelativeView(FormView):
    """
    This object deal with forms and views with two db models.
    """

    def __init__(self, form_name, request, relative_forms):
        """
        Set form name and request.

        Args:
            form_name: model form's name
            request: http request

        Returns:
            None
        """
        super(RelativeView, self).__init__(form_name, request)

        # set relative forms's names
        self.relative_forms = relative_forms
        self.relative_data = {}

    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        if not super(RelativeView, self).parse_request():
            return False

        self.template_file = getattr(self.form_class.Meta, "form_template", "relative_form.html")

        # Check relative form's name.
        for typeclass, form_name in self.relative_forms.iteritems():
            try:
                forms.Manager.get_form(form_name)
            except Exception, e:
                logger.log_tracemsg("Invalid form %s: %s." % (form_name, e))
                self.error = "Invalid form: %s." % form_name
                return False

        return True

    def query_view_data(self):
        """
        Get db instance for view.

        Returns:
            None
        """
        super(RelativeView, self).query_view_data()

        # Get relative form's data.
        self.relative_data = {}
        for typeclass, form_name in self.relative_forms.iteritems():
            relative_class = forms.Manager.get_form(form_name)
            data = None
            if self.key:
                try:
                    relative_instance = relative_class.Meta.model.objects.get(key=self.key)
                    data = relative_class(instance=relative_instance)
                except Exception, e:
                    data = None

            if not data:
                data = relative_class()

            self.relative_data[typeclass] = data

    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        context = super(RelativeView, self).get_context()

        # Set relative form's context.
        relative_data = [({"typeclass": key, "data": self.relative_data[key]}) for key in self.relative_data]
        relative_typeclasses = list(self.relative_forms)

        context["relative_data"] = relative_data
        context["relative_typeclasses"] = relative_typeclasses

        return context

    def query_submit_data(self):
        """
        Get db instance to submit a record.

        Returns:
            None
        """
        super(RelativeView, self).query_submit_data()

        # Get relative form's data.
        self.relative_data = {}
        for typeclass, form_name in self.relative_forms.iteritems():
            relative_class = forms.Manager.get_form(form_name)
            data = None
            if self.key:
                try:
                    relative_instance = relative_class.Meta.model.objects.get(key=self.key)
                    data = relative_class(self.request_data, instance=relative_instance)
                except Exception, e:
                    data = None

            if not data:
                data = relative_class(self.request_data)

            self.relative_data[typeclass] = data


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

        # Validate
        saved = False
        typeclass = self.request_data["typeclass"]
        if typeclass not in self.relative_data:
            if self.data.is_valid():
                with transaction.atomic():
                    self.data.save()
                    # Keep old lock data, comment following codes.
                    # if lock_instance:
                    #     lock_instance.delete()
                    saved = True
        else:
            # Prevent short cut.
            base_valid = self.data.is_valid()
            relative_valid = self.relative_data[typeclass].is_valid()

            if base_valid and relative_valid:
                with transaction.atomic():
                    self.data.save()
                    self.relative_data[typeclass].save()
                    saved = True

        if saved and "_save" in self.request_data:
            # save and back
            return self.quit_form()

        return self.view_form()


    def delete_form(self):
        """
        Delete a record.

        Returns:
            HttpResponse
        """
        super(RelativeView, self).delete_form()

        # Delete relative data.
        if self.key:
            for typeclass, form_name in self.relative_forms.iteritems():
                relative_class = forms.Manager.get_form(form_name)
                try:
                    instance = relative_class.Meta.model.objects.get(key=self.key)
                    instance.delete()
                except Exception, e:
                    pass

        return self.quit_form()