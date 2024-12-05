from django.shortcuts import render
from django.http import JsonResponse
from txtai.embeddings import Embeddings
import logging
from .services.index import (
                    read_file_index_ranges,
                    save_file_index_ranges,
                    )
from .services.openai import (
                    send_response,
                    send_error
                    )
from .helper.text_extract import (
                    split_text,
                    )

def append_new_embedding_data_to_brain(filename,content,source_fold,temp_index_path,brainName):
    """
    Appends new embedding data to the brain.
    
    Args: 
        filename (str): The name of the file containing the new data.
        content (str): The content to be embedded.
        source_fold (str): The source folder path.
        temp_index_path (str): The path of the temporary index file.
        brainName (str): The name of the brain to update.
        
    Returns:
        JsonResponse: Error response if embedding loading or appending fails.
    """

    word_chunks = split_text(content, 100)
    for i in range(len( word_chunks)):
        string=""
        for x in word_chunks[i]:
            string = string+x+" "
        word_chunks[i] =string
    temp_dict = (read_file_index_ranges(brainName))
    counter_index = temp_dict['last_index']
    first_index = counter_index+1

    embedding = Embeddings(hybrid =True,content=True)

    try:
        embedding.load(temp_index_path)
        logging.info(f"For BrainID - {brainName}, Embedding Loaded From {temp_index_path}")
    except Exception as e:
        logging.error(f"For BrainID - {brainName}, Failed To Load Embedding Index To {temp_index_path}")
        return send_error(data=[str(e)], message= "Failed to load information to server", status=500)

    try:
        for x in word_chunks:
            counter_index+=1
            embedding.upsert([(counter_index,x,"filename")])
    except Exception as e:
        logging.error(f'error : {str(e)}')
        return send_error(data=str(e), message="Failed to append information",status=500)
    
    temp_dict['last_index'] = counter_index
    file_dict = temp_dict['files'] 
    file_dict[f'{filename}'] = [first_index,counter_index]
    temp_dict['files'] = file_dict
    embedding.save(temp_index_path)
    save_file_index_ranges(brainName,temp_dict)


def create_embeddings(filename,content,source_fold,target_folder,brainName):
    """
    Creates embeddings from the provided content and saves them to the target folder.
    
    Args: 
        filename (str): The name of the file containing the data.
        content (str): The content to be embedded.
        source_fold (str): The source folder path.
        target_folder (str): The path to save the embedding index.
        brainName (str): The name of the brain to update.
    
    Returns:
        None
    """
    embeddings = Embeddings(hybrid =True,content=True)

    word_chunks = split_text(content, 100)
    for i in range(len( word_chunks)):
        string=""
        for x in word_chunks[i]:
            string = string+x+" "
        word_chunks[i] =string
    txtai_data=[]
    
    i=0
    for x in word_chunks:
        i+=1
        txtai_data.append((i,(x),None))
    temp_dict = read_file_index_ranges(brainName)
    temp_dict['last_index'] = i
    file_dict ={}
    file_dict[f'{filename}'] = [0,i]
    temp_dict['files'] =  file_dict
    save_file_index_ranges(brainName,temp_dict)
    
    embeddings.index(txtai_data)
    embeddings.save(target_folder)


def delete_embedding_data(start_range,end_range,temp_index_path,brainName):
    """
    Deletes embedding data within the specified range from the brain.
    
    Args: 
        start_range (int): The starting index of the range to delete.
        end_range (int): The ending index of the range to delete.
        temp_index_path (str): The path to the temporary index file.
        brainName (str): The name of the brain to update.
    
    Returns:
        None
    """
    embedding = Embeddings(hybrid =True,content=True)
    try:
        embedding.load(temp_index_path)
        logging.info(f"For BrainID - {brainName}, Embedding Loaded From {temp_index_path}")
    except Exception as e:
        logging.error(f"For BrainID - {brainName}, Failed To Load Embedding Index To {temp_index_path}")
        return send_error(data=[str(e)], message= "Failed to Load information in server folder" ,status=500)
    
    for i in range(start_range,end_range+1):
        try:
            r= embedding.delete([i])
            if len(r)>0:
                if int(r[0]) ==i:
                    logging.info(f"For BrainID - {brainName}, Embedding Deleted For {i} {temp_index_path}")

        except Exception as e:
            logging.error(f"For BrainID - {brainName}, Failed To Delete Index {i} for brain in {temp_index_path} {e}")
    embedding.save(temp_index_path)
        

    