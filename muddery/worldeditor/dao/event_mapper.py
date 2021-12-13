"""
Query and deal common tables.
"""

from muddery.worldeditor.dao import general_query_mapper as query


def get_element_event(element_key):
    """
    Get object's event.
    """
    return query.filter_records("event_data", trigger_obj=element_key)
