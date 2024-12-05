import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
from personadjango.services.s3 import (
    check_if_brain_persist_in_s3,
    rename_s3_brain_folders,
    delete_folder_from_s3
)
from personadjango.services.index import (
    rename_local_index_file
)
from personadjango.services.openai import send_error, send_response

@csrf_exempt
def renamebrain(request):
    """
    Rename the brain from old_brainName to new_brainName across the system.

    Args:
        request (HttpRequest): The HTTP request object containing old_brainName and new_brainName.

    Returns:
        JsonResponse: The response indicating the success or failure of renaming.
    """
    if request.method != 'POST':
        return send_error(data=["Only POST method is allowed"], message="Method Not Allowed!", status=405)

    old_brainName = request.POST.get('old_brainName')
    new_brainName = request.POST.get('new_brainName')

    # Validate old_brainName and new_brainName
    if not old_brainName or not old_brainName.strip():
        logging.error('Old brain name cannot be empty')
        return send_error(data=["Empty Parameter: old_brainName"], message="old_brainName required!")
    if not new_brainName or not new_brainName.strip():
        logging.error('New brain name cannot be empty')
        return send_error(data=["Empty Parameter: new_brainName"], message="new_brainName required!")

    # Check if old_brainName exists in S3
    if not check_if_brain_persist_in_s3(old_brainName):
        logging.error(f'Brain {old_brainName} does not exist in S3')
        return send_error(data=[f"Brain {old_brainName} does not exist in S3"], message="Brain Not Found", status=404)

    # Check if new_brainName already exists
    if check_if_brain_persist_in_s3(new_brainName):
        logging.error(f'Brain {new_brainName} already exists in S3')
        return send_error(data=[f"Brain {new_brainName} already exists in S3"], message="Brain Name Conflict", status=409)

    try:
        # 1. Rename the S3 folder in both master_doc_repo and master_index_repo
        rename_s3_brain_folders(old_brainName, new_brainName)

        # 2. Rename the local file index JSON file
        rename_local_index_file(old_brainName, new_brainName)

        logging.info(f'Brain {old_brainName} successfully renamed to {new_brainName}')

    except Exception as e:
        logging.error(f'Error renaming brain: {e}')
        return send_error(data=[str(e)], message="Failed to rename brain", status=500)


    try:
        delete_folder_from_s3(old_brainName)
        return send_response(data=[f"Brain {old_brainName} renamed to {new_brainName}"], message=f"Brain {old_brainName} successfully renamed to {new_brainName}", status=200)
    except KeyError:
        logging.error(f"Old brain does not present in s3")
        return send_error(data=[f"Old brain does not present in s3."], message="Brain not present!", status=404)
    except Exception as e:
        logging.error(f"Failed to delete '{old_brainName}' from s3")
        return send_error(data=[f"Failed to delete '{old_brainName}' from s3."], message="Failed Clearing!", status=500)
