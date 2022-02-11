
import tempfile


async def parse_file(request):
    # Get file in the request
    return request.files["file"][0].body, request.files["file"][0].name
