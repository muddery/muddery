
"""
This file checks user's edit actions and put changes into db.
"""

from django import http
from django.http import HttpResponseRedirect
from django.db import transaction
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.worlddata.editor.form_view import FormView
from muddery.worlddata.data_sets import DATA_SETS
from worlddata import forms


class RelativeView(FormView):
    """
    This object deal with forms and views with two db models.
    """

    def __init__(self, form_name, request, relative_form_names):
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
        self.relative_form_names = relative_form_names
        self.relative_forms = {}

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
        for typeclass, form_name in self.relative_form_names.iteritems():
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
        self.relative_forms = {}
        for typeclass, form_name in self.relative_form_names.iteritems():
            relative_form_class = forms.Manager.get_form(form_name)
            relative_form = None
            if self.key:
                try:
                    relative_instance = relative_form_class.Meta.model.objects.get(relation=self.key)
                    relative_form = relative_form_class(instance=relative_instance)
                except Exception, e:
                    relative_form = None

            if not relative_form:
                relative_form = relative_form_class()

            self.relative_forms[typeclass] = relative_form

    def get_context(self):
        """
        Get render context.

        Returns:
            context
        """
        context = super(RelativeView, self).get_context()

        # Set relative form's context.
        relative_data = [({"typeclass": key, "data": self.relative_forms[key]}) for key in self.relative_forms]
        relative_typeclasses = list(self.relative_form_names)

        context["relative_data"] = relative_data
        context["relative_typeclasses"] = relative_typeclasses
        
        # area
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

    def submit_form(self):
        """
        Edit a record.

        Returns:
            HttpResponse
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        # Query data.
        if not self.form:
            self.query_submit_data()

        # Validate
        saved = False
        typeclass = self.request_data["typeclass"]
        if typeclass not in self.relative_form_names:
            if self.form.is_valid():
                with transaction.atomic():
                    self.form.save()
                    # Keep old lock data, comment following codes.
                    # if lock_instance:
                    #     lock_instance.delete()
                    saved = True
        else:
            # Get relative form data.            
            with transaction.atomic():
                # Prevent short cut.
                if self.form.is_valid():
                    instance = self.form.save()
                    key = instance.key

                    # set relative form data
                    form_name = self.relative_form_names[typeclass]
                    relative_form_class = forms.Manager.get_form(form_name)
                    relative_form = None

                    data = dict(self.request_data)
                    for data_key in data:
                        if data[data_key]:
                            data[data_key] = data[data_key][0]

                    try:
                        relative_instance = relative_form_class.Meta.model.objects.get(key=key)
                        relative_form = relative_form_class(data, instance=relative_instance)
                    except Exception, e:
                        # Add key
                        data["key"] = key
                        relative_form = relative_form_class(data)

                    if relative_form.is_valid():
                        relative_form.save()
                        self.relative_forms[typeclass] = relative_form
                        saved = True

        if saved and "_save" in self.request_data:
            # save and back
            return self.quit_form()

        return self.view_form()

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

    def delete_form(self):
        """
        Delete a record.

        Returns:
            HttpResponse
        """
        super(RelativeView, self).delete_form()

        # Delete relative data.
        if self.key:
            for typeclass, form_name in self.relative_form_names.iteritems():
                relative_class = forms.Manager.get_form(form_name)
                try:
                    instance = relative_class.Meta.model.objects.get(key=self.key)
                    instance.delete()
                except Exception, e:
                    pass

        return self.quit_form()