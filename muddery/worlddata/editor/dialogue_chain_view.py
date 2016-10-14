
"""
This file checks user's edit actions and put changes into db.
"""

import re
from django import http
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.db.models.fields.related import ManyToOneRel
from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.worlddata.editor.form_view import FormView
from worlddata import forms


class DialogueChainView(FormView):
    """
    This object deal with dialogue relation's edit forms and views.
    """

    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        if not super(DialogueChainView, self).parse_request():
            return False

        # self.template_file = getattr(self.form_class.Meta, "form_template", "dialogue_chain_form.html")
        return True
