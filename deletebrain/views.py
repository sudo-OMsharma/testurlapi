import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from personadjango.services.s3 import (
                                check_if_brain_persist_in_s3, 
                                delete_folder_from_s3,                                
                                )
from personadjango.services.openai import (
                                send_error,
                                send_response
                                )
@csrf_exempt
def deletebrain(request):
    """
    Handle the deletion of a brain from both RAM and S3 storage.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: The response indicating the success or failure of brain deletion.
    """
    if request.method != 'POST':
        return send_error(data=["Any method beside POST is not allowed"], message="Method not allowed!", status=405)
    
    # Get the brainName parameter from the POST request
    brainName = request.POST.get('brainName')
    if not brainName:
        logging.error("Brain name is required but was not provided")
        return send_error(data=["brainName parameter value is empty"], message="Empty Parameter: brainName!")

    # # Attempt to delete the brain from RAM
    try:
        del settings.MASTER_EMBEDDING_ARRAY[brainName]
        logging.info(f"For BrainID - {brainName}, Runtime Index deleted from memory")
    except KeyError:
        logging.warning(f"For BrainID - {brainName}, Runtime Index not present in memory")
    except Exception as e:
        logging.error(f"For BrainID - {brainName}, Failed to delete Runtime Index from memory: {str(e)}")
        return send_error(data=["Failed to delete runtime index from memory (failed in deletion of brain from RAM)"], message="Brain deletion failed from RAM!", status=500)

    # Attempt to delete from S3
    if check_if_brain_persist_in_s3(brainName):
        try:
            delete_folder_from_s3(brainName)
            logging.info(f'Deleted brain {brainName} from S3')
            return send_response(data=[f"Brain {brainName} deleted successfully from both memory and S3."], message="Brain Deleted!")
        except Exception as e:
            logging.error(f'Error deleting brain {brainName} from S3: {str(e)}')
            return send_error(data=["Failed to delete brain from S3", str(e)], message="Brain deletion failed from storage!", status=500)
    else:
        logging.info(f"Brain {brainName} not found in S3")
        return send_error(data=["Brain does not exists in S3 (storage system)"], message="Brain not found!", status=404)

