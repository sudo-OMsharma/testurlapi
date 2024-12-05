import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from personadjango.services.openai import (
                            send_error,
                            send_response
                            )
@csrf_exempt
def del_embedding_from_runtime(request):
    """
    View function to delete embeddings from runtime memory based on POST requests.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: JSON response indicating success or failure of the operation.
    """
    if request.method != 'POST':
        return send_error(data=["Any method beside POST is not allowed"], message=-"Method not allowed!", status=405)
    
    # Get the brainName parameter from the POST request
    brainName = request.POST.get('brainName')

    # If brainName is not provided, clear all brain indexes from memory
    if not brainName:
        try:
            settings.MASTER_EMBEDDING_ARRAY = {}
            logging.info("All Brain Indexes Removed From Memory")
            return send_response(data=["All brain indexes removed from memory."], message="Cleared!")
        except Exception as e:
            logging.error("Failed to clear all brain indexes from memory")
            return send_error(data=["Failed to clear all brain indexes from memory."], message="Failed Clearing!", status=500)
    else:
        logging.info(f"For BrainID - {brainName}, Delete Runtime Index API Called")
        try:
            del settings.MASTER_EMBEDDING_ARRAY[brainName]
            logging.info(f"Runtime index for '{brainName}' deleted from memory")
            return send_response(data=[f"Runtime index for '{brainName}' deleted from memory."], message="Cleared!")
        except KeyError:
            logging.error(f"Runtime index for '{brainName}' not present in memory")
            return send_error(data=[f"Runtime index for '{brainName}' not present in memory."], message="Brain not present!", status=404)
        except Exception as e:
            logging.error(f"Failed to delete runtime index for '{brainName}' from memory")
            return send_error(data=[f"Failed to delete runtime index for '{brainName}' from memory."], message="Failed Clearing!", status=500)

