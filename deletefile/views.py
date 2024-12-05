import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from personadjango.services.s3 import ( 
                                download_files_from_s3, 
                                upload_folder_to_s3,
                                delete_file_from_s3,
                                upload_content_from_fileindexrange_to_s3,
                                )
from personadjango.services.index import (
                                read_file_index_ranges, 
                                save_file_index_ranges, 
                                delete_folder_content
                                )
from personadjango.services.openai import (
                                send_error,
                                send_response
                                )
from personadjango.embeddings import delete_embedding_data

load_dotenv()

@csrf_exempt
def del_file(request):
    """
    Handle the deletion of specified files for a given brain from both local storage and S3.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: The response indicating the success or failure of file deletion.
    """
    if request.method != 'POST':
        return send_error(data=["Any method beside POST is not allowed"], message="Method not allowed!", status=405)
    
    brainName = request.POST.get('brainName')
    file_names = request.POST.getlist('file_names')  # Expecting a list of file names
    
    # Check if brainName and file_names are provided
    if not brainName or not file_names:
        logging.error("Brain name and file names are required")
        return send_error(data=["brainName or file_names parameter value is empty"], message="Empty parameter: brainName or file_names!")
    
    # Define the temporary index path for storing downloaded files
    temp_index_path = os.path.join(os.environ.get('TEMP_INDEX_STORAGE'), brainName)
    os.makedirs(temp_index_path, exist_ok=True)
    
    # Download the index files from S3 to the temporary path
    try:
        download_files_from_s3(os.environ.get('BUCKET_NAME'), f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{brainName}", temp_index_path)
    except Exception as e:
        logging.error(f"Failed to download index to {temp_index_path} from S3 bucket: {os.environ.get('BUCKET_NAME')}")
        return send_error(data=[str(e)], message="Downloading of files failed!", status=500)
    
    # Read the file index ranges for the specified brain
    file_index_ranges = read_file_index_ranges(brainName)
    files_to_delete = file_index_ranges.get('files', {})
    deleted_files = []
    not_present_files = []
    
    # Loop through the list of files to be deleted
    for file_name in file_names:
        if file_name in files_to_delete:
            start_val, end_val = files_to_delete[file_name]
            delete_embedding_data(start_val, end_val, temp_index_path, brainName)
            del file_index_ranges['files'][file_name]
            delete_file_from_s3(brainName, file_name)
            deleted_files.append(file_name)
        else:
            not_present_files.append(file_name)
    
    # If files were successfully deleted, update the index and upload changes to S3
    if deleted_files:
        try:
            upload_folder_to_s3(os.environ.get('BUCKET_NAME'), temp_index_path, f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{brainName}")
            save_file_index_ranges(brainName, file_index_ranges)
            upload_content_from_fileindexrange_to_s3(brainName)
        except Exception as e:
            logging.error("Failed during the file update process after deletion")
            return send_error(data=[str(e)], message="Update processing of information of brain after deletion failed!", status=500)
        
    # Clean up the temporary directory
    delete_folder_content(temp_index_path)

    # Return the appropriate response
    if not_present_files and not deleted_files:
        return send_error(data=[f"Not present: {', '.join(not_present_files)}"], message="File not Found!", status=404)
    else:
        message = f"Deleted successfully: {', '.join(deleted_files)}"
        if not_present_files:
            message += f".  Not present: {', '.join(not_present_files)}"
        return send_response(data=[message], message="Operation completed successfully!")

