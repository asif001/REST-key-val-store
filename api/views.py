from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import patchrequesthandler, postrequesthandler, getrequesthandler

# URL format - HOST_NAME/api?keys=key1, key2, ...
# Here key is keys and value is 'key1, key2, ...'


@api_view(['GET', 'POST', 'PATCH'])
def manage_items(request, *args, **kwargs):

    # Handling Get Request #
    if request.method == 'GET':
        response, status_code = getrequesthandler.handle_get_request(request)
        return Response(response, status=status_code)

    # Handling POST Request
    elif request.method == 'POST':
        response, status_code = postrequesthandler.handle_post_request(request)
        return Response(response, status=status_code)

    # Handling PATCH Request
    elif request.method == 'PATCH':
        response, status_code = patchrequesthandler.handle_patch_request(request)
        return Response(response, status=status_code)
