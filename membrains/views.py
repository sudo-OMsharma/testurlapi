import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from personadjango.services.openai import (
                                    send_error,
                                    send_response
                                )
@csrf_exempt
def membrains(request):
    """
    Retrieves and returns `settings.MASTER_EMBEDDING_ARRAY` as a JSON response for GET requests.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: JSON response containing the master embedding array data or an error message.
    """
    if request.method == 'GET':
        try:
            logging.info("Returning master_embedding_array")
            # Convert the embedding array to a string representation for the response if needed
            embedding_info = str(settings.MASTER_EMBEDDING_ARRAY)  # Assuming this is how you want to display the data
            return send_response(data=[embedding_info], message="Displayed!")
        except Exception as e:
            logging.error("Failed to retrieve master_embedding_array")
            return send_error(data=["Failed to retrieve master embedding array"], message="Failed to display!", status=500)
    else:
        logging.error("Method not allowed for the requested operation")
        return send_error(data=["Any method beside POST is not allowed"], message="Method not allowed!", status=405)
