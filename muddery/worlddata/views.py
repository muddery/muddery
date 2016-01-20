
"""
This contains a simple view for rendering the webclient
page and serve it eventual static content.

"""
from __future__ import print_function
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from evennia.players.models import PlayerDB


@staff_member_required
def worldeditor(request):
    """
    World Editor page template loading.
    """
    return render(
        request, 'worldeditor.html')