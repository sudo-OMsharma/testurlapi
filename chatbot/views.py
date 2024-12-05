from django.http import JsonResponse
import logging
import os
from threading import Lock
from dotenv import load_dotenv
from txtai.embeddings import Embeddings
from django.conf import settings
from personadjango.services.s3 import (
                                download_files_from_s3                           
                                )
from personadjango.services.openai import (
                                openai_gpt_chatbot,
                                summarize_previous_qa,
                                send_error,
                                send_response
                                )
from personadjango.services.index import(
                                delete_folder_content,
                                read_file_index_ranges
                                )
from personadjango.helper.text_extract import (
                                search_file_name_from_index,
                                )
from personadjango.helper.emotion import (
                                get_emotion,
                                get_voice_settings,
                                detect_language,
                                payload_return
                                )
from django.views.decorators.csrf import csrf_exempt

# Initialize a lock for controlling access to MASTER_EMBEDDING_ARRAY
master_embedding_locks = {}

# Load environment variables from a .env file
load_dotenv()

def get_lock_for_brain(brainName):
    """
    Get or create a lock for a specific brain.

    Args:
        brainName (str): The name of the brain.

    Returns:
        Lock: A lock object for the specified brain.
    """
    if brainName not in master_embedding_locks:
        master_embedding_locks[brainName] = Lock()
    return master_embedding_locks[brainName]

@csrf_exempt
def chatbot(request):
    """
    Handle chat requests, manage embeddings, and generate response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: The response containing the generated chat message or error.
    """
    if request.method == 'POST':
        # Extract parameters from the POST request
        llm = request.POST.get("llm")
        brainName = request.POST.get('brainName')
        question_asked = request.POST.get('current_user_question')
        response_size = int(request.POST.get('word_limit', 30))
        toxic_filter = request.POST.get('toxic_filter', 'False').lower() in ['true']
        clear = request.POST.get('clear')
        display = request.POST.get('display')
        previous_question = request.POST.get('previous_question')
        previous_answer = request.POST.get('previous_answer')
        
        # Obtain the lock for the specific brainName
        brain_lock = get_lock_for_brain(brainName)
        
        # Clear the entire master embedding array if brainName is not specified
        if clear == 'True' and brainName is None:
            with brain_lock:
                settings.MASTER_EMBEDDING_ARRAY = {}
                logging.info('Cleared master_embedding_array')
            return send_response(data="Cleared master_embedding_array completely", message="Cleared!")
        
        # Clear specific brain from master embedding array
        if clear == 'True':
            with brain_lock:
                settings.MASTER_EMBEDDING_ARRAY.pop(brainName, None)
                logging.info(f"Cleared specific brain '{brainName}' from master_embedding array")
            return send_response(data=f"Cleared {brainName} from master_embedding_array", message="Cleared!")
        
        # Display the current master embedding array
        if display == 'True':
            logging.info("Returning master_embedding_array")
            return send_response(data=str(settings.MASTER_EMBEDDING_ARRAY), message="Displayed!")
        
        # Validate required parameters
        if not llm or llm.split() == '':
            logging.error("llm parameter cannot be empty")
            return send_error(data=["llm parameter's value is empty, it should only be openai"], message="Value of llm parameter cannot be empty, it should be openai!")
        if not brainName or brainName.split() == '':
            logging.error("brainName parameter cannot be empty")
            return send_error(data=["brainName parameter's value is empty"], message="Value of brainName parameter cannot be empty!")
        if not question_asked or question_asked.split() == '':
            logging.error("current_user_question parameter cannot be empty")
            return send_error(data="current_user_question parameter's value is empty", message="Value of current_user_question is empty!")
        
        # Ensure response size is within acceptable limits
        if response_size is None:
            response_size = 30
        elif response_size < 10:
            response_size = 15    

        logging.info(f"For BrainID - {brainName}, Chat API Called")
        logging.info(f"For BrainID - {brainName}, Question Asked : {question_asked}")
        
        # Load personality name for the brain
        try:
            personality_name = read_file_index_ranges(brainName)['personality_name']
            logging.info(f"For BrainID - {brainName}, Loaded Personality Name : {personality_name}")
        except Exception as e:
            logging.error(f"For BrainID - {brainName}, Failed to Load Personality Name")
        
        # Load file index ranges for the brain
        try:
            files_ranges = read_file_index_ranges(brainName)['files']
            logging.info(f"For BrainID - {brainName}, Loaded File Index Ranges: {files_ranges}")
        except Exception as e:
            logging.error(f"For BrainID - {brainName}, Failed to Load File Index Ranges")
        
        # If the brain is not in memory, load it
        if brainName not in settings.MASTER_EMBEDDING_ARRAY:
            temp_folder_path = f"{os.environ.get('TEMP_CONNECTION_INDEX_STORAGE')}/{brainName}/"
            if not os.path.exists(temp_folder_path):
                os.makedirs(f'{temp_folder_path}')
                logging.info(f'For BrainID - {brainName}, Temp Index Storage Allocated at - {temp_folder_path}')
            try:
                download_files_from_s3(os.environ.get('BUCKET_NAME'), (f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{brainName}"), temp_folder_path)
                logging.info(f"For BrainID - {brainName}, Index File Content Downloaded From S3 Bucket to {temp_folder_path}")
            except Exception as e:
                logging.error(f"For BrainID - {brainName}, Failed To Download Index To {temp_folder_path} from S3 Bucket - {os.environ.get('BUCKET_NAME')}")
                return send_error(data=str(e), message="Failed to load brain in memory!", status=500)

            embedding_name = Embeddings(hybrid=True)
            try:
                embedding_name.load(temp_folder_path)
                logging.info(f"For BrainID - {brainName}, Embedding Loaded From {temp_folder_path}")
            except Exception as e:
                logging.error(f"For BrainID - {brainName}, Failed To Load Embedding Index To {temp_folder_path}")
                return send_error(data="Brain or Brain Index Does not exist", message="Brain does not exist!", status=404)

            delete_folder_content(temp_folder_path)

            with brain_lock:   # Ensure thread-safe access to MASTER_EMBEDDING_ARRAY
                if len(settings.MASTER_EMBEDDING_ARRAY) == 0:
                    settings.MASTER_EMBEDDING_ARRAY = {
                        f'{brainName}': {
                            f'{brainName}': embedding_name,
                            f'personality_name': personality_name,
                            f'files': files_ranges
                        }
                    }
                else:       # Add the brain's embedding to the existing array
                    settings.MASTER_EMBEDDING_ARRAY[brainName] = {
                        f'{brainName}': embedding_name,
                        f'personality_name': personality_name,
                        f'files': files_ranges
                    }
                logging.info(f"For BrainID - {brainName}, Index Loaded In RunTime - {embedding_name}")

        summarize_text = summarize_previous_qa(previous_question, previous_answer)  
        toxic_filter_value = toxic_filter  
        try:
            if toxic_filter:
                toxic_filter = "For each identified toxic word in prompt, Strictly retain the first and last letter of the toxic word and replace all in-between letters of the toxic word with asterisks (*). Toxic words you must consider are profanity, swear words, hate speech, sexual content, violent and threatenining words, insults and slurs, vulgar expressions, sexual orientation (e.g., 'gay', 'lesbian'), disability, or appearance, inappropriate or disprespectful language (e.g., 'lazy ass'), and any other phrases considered rude, disrespectful, or hurtful in any social or cultural context."
            else:
                toxic_filter = None
        except Exception as e:
            logging.error(f"Failed to Initialize toxic filter")
        try:
            with brain_lock:  # Ensure thread-safe search
                output = " "
                if "you" in question_asked.lower():
                    question_asked_txtai = question_asked + f"I am {personality_name}"
                else:
                    question_asked_txtai = summarize_text + question_asked
                res = settings.MASTER_EMBEDDING_ARRAY[brainName][brainName].search(question_asked_txtai, 7)
                logging.info(f"For BrainID - {brainName}, Search Result : {res}")
                dict = settings.MASTER_EMBEDDING_ARRAY[brainName]['files']
                for i in range(0, len(res)):
                    file_name = search_file_name_from_index(dict, int(res[i]['id']))
                    output = output + (file_name) + " --> " + (res[i]['text']) + "\n"

                question_asked_log  = question_asked_txtai
                if llm == "openai" or llm is None:
                    answer = openai_gpt_chatbot(question_asked_log, personality_name, response_size, output, question_asked, toxic_filter)
                    logging.info(f"For BrainID - {brainName}, For Question - {question_asked_log} ,Response Generated - '{answer}'")
                    
                    emotion = get_emotion(answer)   # Analyze emotion of the answer
                    language = detect_language(question_asked)
                    payload_elevenlabs = payload_return(answer, emotion, language, toxic_filter_value)

                    return send_response(data=payload_elevenlabs, message="Response Generated Successfully!")
                else:
                    return send_error(data="llm value should only be openai", message="llm value should be openai!")

        except Exception as e:
            logging.error(f"For BrainID - {brainName},Query - {question_asked_log}, Failed Search On Embedding {settings.MASTER_EMBEDDING_ARRAY[brainName]}")
            return send_error(data=str(e),message="Unable to generate response!", status=500)
    else:
        return send_error(data="Any method except POST is not not allowed", message="Method not allowed!", status=405)