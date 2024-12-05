import os
import logging
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseBadRequest
from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from personadjango.services.s3 import (
    download_files_from_s3, 
    upload_folder_to_s3, 
    check_if_brain_persist_in_s3, 
    check_content_in_s3_folder, 
    upload_file_to_s3, 
    upload_content_from_fileindexrange_to_s3,
)
from personadjango.services.index import (
    delete_folder_content, 
    read_file_index_ranges,
)
from personadjango.services.openai import (
    send_error,
    send_response,
    whisper_transcription
)
from personadjango.embeddings import (
    create_embeddings, 
    append_new_embedding_data_to_brain
) 
from personadjango.helper.text_extract import (
    load_all_text,
)        
from personadjango.helper.transcriptions import (
    convert_video_to_audio,
    save_transcription_to_file
)

load_dotenv()

@csrf_exempt
def upload_file(request):
    """
    Handles file upload and processing for a specified brainName using AWS S3 and local storage.

    Args:
        request (HttpRequest): The HTTP request object containing 'brainName' and 'file' parameters.

    Returns:
        JsonResponse: JSON response indicating the status of each uploaded file and processing steps.
    """
    if request.method == 'POST':
        brainName = request.POST.get('brainName')

        if not check_if_brain_persist_in_s3(brainName) or not brainName:
            return send_error(data=["Brain does not exist or brainName parameter value is empty"], message='Brain does not exist or Empty parameter: brainName!', status=404)

        files = request.FILES.getlist('file')
        if not files:
            return send_error(data=["No files are provided"], message='No files provided!')

        responses = []

        for file in files:
            filename = file.name
            flag = True
            if not filename:
                logging.error(f'For BrainID - {brainName}, File Content Is None')
                responses.append({'filename': filename, 'status': 'No selected file'})
                continue
            if not filename.endswith((".txt", ".pdf", ".docx", ".mp3", ".wav", ".ogg", ".mov", ".mp4", ".mkv")):
                logging.error(f'Unsupported File Format for {filename}')
                responses.append({'filename': filename, 'status': 'Unsupported file format'})
                flag = False
                continue
            
            if flag == True:
                # Handle audio and video files
                generated_txt_file = None
                if filename.endswith((".mp3", ".wav", ".ogg", ".mov", ".mp4", ".mkv")):
                    temp_folder_path = f"{os.environ.get('TEMP_FILE_STORAGE')}/{brainName}/"
                    if not os.path.exists(temp_folder_path):
                        os.makedirs(temp_folder_path)
                        logging.info('Temporary folder created')

                    fs = FileSystemStorage(location=temp_folder_path)
                    file_path = fs.save(filename, file)

                    # Process the audio or video file
                    audio_file_path = f"{temp_folder_path}/{filename}"
                    if filename.endswith((".mov", ".mp4", ".mkv")):
                        video_file_path = f"{temp_folder_path}/{filename}"
                        audio_file_path = f"{temp_folder_path}/{filename}.mp3"
                        convert_video_to_audio(video_file_path, audio_file_path)
                    else:
                        audio_file_path = audio_file_path

                    # Transcribe the audio file
                    try:
                        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY_1'))
                        extracted_text = whisper_transcription(audio_file_path, client)
                        logging.info('Transcription generated')
                        os.remove(audio_file_path)
                    except Exception as e:
                        logging.error(f'Error transcribing audio: {e}')
                        os.remove(audio_file_path)
                        responses.append({'filename': filename, 'status': 'Error transcribing audio'})
                        continue

                    # Save the transcription to a text file
                    text_file_path = f"{temp_folder_path}/{os.path.splitext(filename)[0]}.txt"
                    save_transcription_to_file(extracted_text, text_file_path)
                    logging.info(f'Transcription saved to {text_file_path}')
                    generated_txt_file = text_file_path
                
                # Use generated text file if available, otherwise use the uploaded file
                if generated_txt_file:
                    file_path = generated_txt_file
                    filename = os.path.basename(generated_txt_file)
                    temp_folder_path = f"{os.environ.get('TEMP_FILE_STORAGE')}/{brainName}/"
                    if not os.path.exists(temp_folder_path):
                        os.makedirs(temp_folder_path)
                        logging.info('Temporary folder created')

                    temp_index_path = f"{os.environ.get('TEMP_INDEX_STORAGE')}/{brainName}"
                    if not os.path.exists(temp_index_path):
                        os.makedirs(temp_index_path)
                        logging.info('Temporary index folder created')
                else:
                    temp_folder_path = f"{os.environ.get('TEMP_FILE_STORAGE')}/{brainName}/"
                    if not os.path.exists(temp_folder_path):
                        os.makedirs(temp_folder_path)
                        logging.info('Temporary folder created')

                    temp_index_path = f"{os.environ.get('TEMP_INDEX_STORAGE')}/{brainName}"
                    if not os.path.exists(temp_index_path):
                        os.makedirs(temp_index_path)
                        logging.info('Temporary index folder created')

                    # File saving
                    fs = FileSystemStorage(location=temp_folder_path)
                    file_path = fs.save(filename, file)

                # Process text files
                temp_dict = read_file_index_ranges(brainName)
                existing_files = temp_dict.get('files', [])
                if filename in existing_files:
                    responses.append({'filename': filename, 'status': 'File already exists'})
                    continue

                text, flag = load_all_text(temp_folder_path)
                logging.info(f'Flag is - {flag}')
                if flag:
                    delete_folder_content(temp_folder_path)
                    responses.append({'filename': filename, 'status': text})
                    continue

                # Process each file
                array = os.listdir(temp_folder_path)

                if check_content_in_s3_folder(brainName):
                    for x in array:
                        file_path_to_upload = f'{temp_folder_path}/{x}'
                        try:
                            upload_file_to_s3(file_path_to_upload, os.environ.get('BUCKET_NAME'), brainName, x)
                        except Exception as e:
                            logging.error(f'Error uploading file to S3: {e}')
                            responses.append({'filename': filename, 'status': str(e)})
                            continue
                    
                    try:
                        download_files_from_s3(os.environ.get('BUCKET_NAME'), f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{brainName}", temp_index_path)
                        logging.info(f"For BrainID - {brainName}, Index File Content Downloaded From S3 Bucket to {temp_index_path}")
                    except Exception as e:
                        logging.error(f"For BrainID - {brainName}, Failed To Download Index To {temp_index_path} from S3 Bucket - {os.environ.get('BUCKET_NAME')}")
                        responses.append(f"For BrainID - {brainName}, Failed To Download Index To {temp_index_path} from S3 Bucket - {os.environ.get('BUCKET_NAME')}")
                        continue
                    
                    append_new_embedding_data_to_brain(filename, text, temp_folder_path, temp_index_path, brainName)
                    logging.info('File retraining completed')
                else:
                    for x in array:
                        file_path_to_upload = f'{temp_folder_path}/{x}'
                        try:
                            upload_file_to_s3(file_path_to_upload, os.environ.get('BUCKET_NAME'), brainName, x)
                        except Exception as e:
                            responses.append(f"error:{e}")
                            continue
                    try:
                        create_embeddings(filename, text, temp_folder_path, temp_index_path, brainName)
                        logging.info(f'For BrainID- {brainName}, Index Generated at {temp_index_path}')
                    except Exception as e:
                        logging.error(f'Error processing {filename}: {str(e)}')
                        responses.append({'filename': filename, 'status': 'Error processing file'})
                        continue

                # Cleanup
                delete_folder_content(temp_folder_path)

                # Update response
                responses.append({'filename': filename, 'status': 'File uploaded and processed successfully'})

            # Upload index to S3 after all files are processed
            try:
                upload_folder_to_s3(os.environ.get('BUCKET_NAME'), temp_index_path, f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{brainName}")
                logging.info(f'Index uploaded for brain {brainName}')
            except Exception as e:
                logging.error(f'Index upload failed for brain {brainName}: {str(e)}')
                responses.append(f'Index upload failed for brain {brainName}: {str(e)}')
            
            delete_folder_content(temp_index_path)
            upload_content_from_fileindexrange_to_s3(brainName)
        return send_response(data=[responses], message="Upload finished!", status=201)
    
    else:
        return send_error(data=["Any method beside POST is not allowed"], message="Method not allowed!", status=405)
