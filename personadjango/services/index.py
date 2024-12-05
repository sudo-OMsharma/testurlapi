import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

def read_file_index_ranges(brainName):
    """
    Read file index ranges from a JSON file.
    
    Args: 
        brainName (str): The name of the brain for which the index ranges are to be read.
        
    Returns:
        dict: A dictionary containing file index.
    """
    file_path = f"{os.environ.get('FILE_INDEX_RANGE')}/{brainName}.json"
    logging.info(f'Reading file index ranges from {file_path}')
    try:
        with open(file_path, 'r') as file:
            logging.info(f'File index ranges successfully read')
            return json.load(file)
    except Exception as e:
        logging.error(f'Error reading file index ranges from {file_path}: {e}')
        raise e

def save_file_index_ranges(brainName, dict):
    """
    Save file index ranges to a JSON file. 
    
    Args:
        brainName (str): The name of the brain for which the index ranges are to be saved.
        dict (dict): A dictionary containing file index ranges.
    """
    file_path = f"{os.environ.get('FILE_INDEX_RANGE')}/{brainName}.json"
    logging.info(f'Saving file index ranges to {file_path}')
    try:
        with open(file_path, 'w') as file:
            json.dump(dict, file)
        logging.info('File index ranges successfully saved')
    except Exception as e:
        logging.error(f'Error saving file index ranges to {file_path}: {e}')
        raise

def delete_folder_content(folder_path):
    """
    Delete all content in a folder and then remove the folder.
    
    Args:
        folder_path (str): The path to the folder to be deleted.
    """
    logging.info(f'Deleting content of folder {folder_path}')
    try:
        for file_name in os.listdir(folder_path):
            os.remove(f'{folder_path}/{file_name}')
        os.rmdir(folder_path)
        logging.info(f'Content of folder {folder_path} successfully deleted')
    except Exception as e:
        logging.error(f'Error deleting folder content for {folder_path}: {e}')
        raise

def rename_local_index_file(old_brainName, new_brainName):
    """
    Rename the local file index JSON file from old_brainName to new_brainName.

    Args:
        old_brainName (str): The old brain name.
        new_brainName (str): The new brain name.
    """
    old_file_path = f"{os.environ.get('FILE_INDEX_RANGE')}/{old_brainName}.json"
    new_file_path = f"{os.environ.get('FILE_INDEX_RANGE')}/{new_brainName}.json"

    logging.info(f'Renaming file index from {old_file_path} to {new_file_path}')
    
    # Read the existing file index
    index_data = read_file_index_ranges(old_brainName)

    # Optionally update any internal references
    if 'brainName' in index_data:
        index_data['brainName'] = new_brainName

    # Save the new file index
    save_file_index_ranges(new_brainName, index_data)

    # Delete the old file
    os.remove(old_file_path)
    logging.info(f"Old index file {old_file_path} deleted successfully")