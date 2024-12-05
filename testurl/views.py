import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Helper functions for sending responses
def send_response(data=None, message="Success", status=200):
    """Standardized success response."""
    return JsonResponse({'message': message, 'data': data}, status=status)

def send_error(data=None, message="Error", status=400):
    """Standardized error response."""
    return JsonResponse({'message': message, 'data': data}, status=status)


@csrf_exempt
def process_url(request):
    """
    Handle a POST request that includes a URL and return it in the response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: The response containing the URL or an error message.
    """
    if request.method != 'POST':
        return send_error(data=["Any method beside POST is not allowed"], message="Method Not Allowed!", status=405)
    
    input_url = request.POST.get('url-test')


    if not input_url or not input_url.strip():
        logging.error('URL cannot be empty')
        return send_error(data=["Empty Parameter: input_url"], message="URL required!", status=400)

    try:        
        logging.info(f"URL successfully processed: {input_url}")
        return send_response(data={"url": input_url}, message="URL processed successfully!", status=200)
    except Exception as e:
        logging.error(f'Error processing URL: {e}')
        return send_error(data=[str(e)], message="Failed to process URL!", status=500)
