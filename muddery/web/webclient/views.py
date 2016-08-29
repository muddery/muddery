
"""
This contains a simple view for rendering the webclient
page and serve it eventual static content.

"""
from __future__ import print_function
from django.shortcuts import render


def webclient(request):
    """
    Webclient page template loading.
    """

    # analyze request to find which port we are on
    if int(request.META["SERVER_PORT"]) == 8000:
        # we relay webclient to the portal port
        print("Called from port 8000!")
        #return redirect("http://localhost:8001/webclient/", permanent=True)

    return render(request, 'webclient.html')
