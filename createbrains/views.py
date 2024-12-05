import logging
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from personadjango.services.s3 import (
                                check_if_brain_persist_in_s3,
                                create_folder_in_s3                                
                                )
from personadjango.services.index import (
                                save_file_index_ranges,
                                )
from personadjango.services.openai import (
                                send_response,
                                send_error
                                )
@csrf_exempt
def createbrains(request):
    """
    Handle the creation of a new brain and its corresponding index in S3.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: The response indicating the success or failure of brain creation.
    """
    if request.method != 'POST':
        return send_error(data=["Any method beside POST is not allowed"], message="Method Not Allowed!", status=405)
    
    # Extract brainName and personality_name from the POST request
    brainName = request.POST.get('brainName')
    personality_name = request.POST.get('personality_name')
    
    # Validate brainName
    if not brainName or not brainName.strip():
        logging.error('Brain name cannot be empty')
        return send_error(data=["Empty Parameter: brainName"], message="brainName required!")
    
    # Validate personality_name
    if not personality_name or not personality_name.strip() or not all((char.isalpha() or char.isspace()) for char in personality_name):
        logging.error('Personality name is missing or has invalid characters')
        return send_error(data=["Invalid or empty parameter: personality_name"], message="Personality name must only contain alphabetic characters and spaces and it should not be empty!", status=400)

    personality_name = personality_name.strip().lower()
    
    # Check if brain already exists in S3
    if check_if_brain_persist_in_s3(brainName):
        logging.error(f'For BrainID - {brainName}, Brain already exists')
        return send_error(data=["Brain already exists in S3 bucket (storage system)"], message="Brain already exists!", status=409)

    try:
        create_folder_in_s3(brainName)
        # Initialize index with personality_name
        temp_dict = {'personality_name': personality_name}
        save_file_index_ranges(brainName, temp_dict)
        logging.info(f'For BrainID - {brainName}, Brain created and file index range saved successfully')
        return send_response(data=["Brain is successfully created in S3 bucket (storage system)"], message="Brain created successfully!", status=201)
    except Exception as e:
        logging.error(f'Failed to create brain for BrainID - {brainName}: {e}')
        return send_error(data=[str(e)], message="Failed to create Brain!", status=500)

