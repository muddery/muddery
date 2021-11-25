
"""
This file contains the generic, assorted views that don't fall under one of
the other applications. Views are django's way of processing e.g. html
templates on the fly.

"""
import traceback

from django.contrib.admin.sites import site
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth import login


def _gamestats():
    # Some misc. configurable stuff.
    # TODO: Move this to either SQL or settings.py based configuration.
    fpage_account_limit = 4

    """
    # A QuerySet of the most recently connected accounts.
    recent_users = AccountDB.objects.get_recently_connected_accounts()[:fpage_account_limit]
    nplyrs_conn_recent = len(recent_users)
    nplyrs = AccountDB.objects.num_total_accounts()
    nplyrs_reg_recent = len(AccountDB.objects.get_recently_created_accounts())
    nsess = SESSION_HANDLER.account_count()
    # nsess = len(AccountDB.objects.get_connected_accounts()) or "no one"

    nobjs = ObjectDB.objects.all().count()
    nrooms = ObjectDB.objects.filter(db_location__isnull=True).exclude(db_typeclass_path=_BASE_CHAR_TYPECLASS).count()
    nexits = ObjectDB.objects.filter(db_location__isnull=False, db_destination__isnull=False).count()
    nchars = ObjectDB.objects.filter(db_typeclass_path=_BASE_CHAR_TYPECLASS).count()
    nothers = nobjs - nrooms - nchars - nexits

    pagevars = {
        "page_title": "Front Page",
        "players_connected_recent": recent_users,
        "num_players_connected": nsess,
        "num_players_registered": nplyrs,
        "num_players_connected_recent": nplyrs_conn_recent,
        "num_players_registered_recent": nplyrs_reg_recent,
        "num_rooms": nrooms,
        "num_exits": nexits,
        "num_objects": nobjs,
        "num_characters": nchars,
        "num_others": nothers
    }
    """

    pagevars = {
        "page_title": "Front Page",
        "num_players_registered": 0,
        "num_players_connected_recent": 0,
        "num_players_registered_recent": 0,
        "num_rooms": 0,
        "num_exits": 0,
        "num_objects": 0,
        "num_characters": 0,
        "num_others": 0
    }
    return pagevars



def page_index(request):
    """
    Main root page.
    """
    # get game db stats
    pagevars = _gamestats()

    try:
        return render(request, 'index.html', pagevars)
    except Exception as e:
        traceback.print_exc()
        raise(e)
