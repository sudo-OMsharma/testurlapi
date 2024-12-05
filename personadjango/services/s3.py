import os
import boto3
import logging
from dotenv import load_dotenv
from django.http import JsonResponse

# Load environment variables from a .env file
load_dotenv()

MASTER_EMBEDDING_ARRAY = {}

def upload_folder_to_s3(bucket, local_folder, to_s3_index_folder):
    """
    Upload all files in a local folder to an S3 bucket.
    
    Args: 
        bucket (str): The name of the S3 bucket.
        local_folder (str): The path to the local folder.
        to_s3_index_folder (str): The target folder path in the S3 bucket.
    """
    logging.info(f'Uploading folder {local_folder} to S3 bucket {bucket} at {to_s3_index_folder}')
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))

        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_key = os.path.join(to_s3_index_folder, os.path.relpath(local_file_path, local_folder))

                # Upload the file to S3
                s3.upload_file(local_file_path, bucket, s3_key)
                logging.info(f'Uploaded {local_file_path} to s3://{bucket}/{s3_key}')
    except Exception as e:
        logging.error(f'Error uploading folder {local_folder} to S3: {e}')
        raise

def check_if_brain_persist_in_s3(folder_name):
    """
    Check if a folder exists in the S3 bucket.
    
    Args:
        folder_name (str): The name of the folder to check.
    
    Returns: 
        bool: True if the folder exists, False otherwise.
    """
    folder_name = f"{os.environ.get('S3_MASTER_DOC_REPO')}/{folder_name}/"
    logging.info(f'Checking if brain persists in S3 folder {folder_name}')
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))

        # Check if the folder exists by listing objects with the specified prefix
        response = s3.list_objects_v2(Bucket=os.environ.get('BUCKET_NAME'), Prefix=folder_name)

        # If there are any objects with the specified prefix, the folder exists
        return 'Contents' in response and len(response['Contents']) > 0
    except Exception as e:
        logging.error(f'Error checking if brain persists in S3: {e}')
        raise

def check_content_in_s3_folder(folder_name):
    """
    Check if a folder in the S3 bucket contains any files.
    
    Args:
        folder_name (str): The name of the folder to check.
    
    Returns:
        bool: True if the folder contains files, False otherwise.
    """
    folder_name = f"{os.environ.get('S3_MASTER_DOC_REPO')}/{folder_name}/"
    logging.info(f'Checking content in S3 folder {folder_name}')
    try:
        file_count, folder_count = 0, 0
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
        response = s3.list_objects_v2(Bucket=os.environ.get('BUCKET_NAME'), Prefix=folder_name)

        if 'Contents' in response and len(response['Contents']) > 0:
            for obj in response['Contents']:
                if obj['Key'].endswith('/'):
                    folder_count += 1
                else:
                    file_count += 1
            logging.info(f'Files: {file_count}, Folders: {folder_count}')
        else:
            return False

        return folder_count != len(response['Contents'])
    except Exception as e:
        logging.error(f'Error checking content in S3 folder {folder_name}: {e}')
        raise

def create_folder_in_s3(folder_name):
    """
    Create a folder in the S3 bucket.
    
    Args: 
        folder_name (str): The name of the folder to create.
    """
    logging.info(f'Creating folder in S3: {folder_name}')
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
        folder_name = f"{os.environ.get('S3_MASTER_DOC_REPO')}/{folder_name}/"
        s3.put_object(Bucket=os.environ.get('BUCKET_NAME'), Key=folder_name)
        logging.info(f'Folder {folder_name} created in S3')
    except Exception as e:
        logging.error(f'Error creating folder in S3: {e}')
        raise

def upload_file_to_s3(file, bucket, brainName, file_name):
    """
    Upload a file to a specific location in the S3 bucket.
    
    Args:
        file (str): The path to the file to upload.
        bucket (str): The name of the S3 bucket.
        brainName (str): The name of the brain to associate with the file.
        file_name (str): The name of the file in the S3 bucket.
    """
    logging.info(f'Uploading file {file} to S3 bucket {bucket} in {brainName}/{file_name}')
    try:
        s3_client = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
        target_path = f'master_doc_repo/{brainName}/{file_name}'
        s3_client.upload_file(file, bucket, target_path)
        logging.info(f'File {file} uploaded to s3://{bucket}/{target_path}')
    except Exception as e:
        logging.error(f'Error uploading file {file} to S3: {e}')
        raise

def download_files_from_s3(bucket, folder, local_path):
    """
    Download all files from a specific folder in the S3 bucket to a local directory.
    
    Args: 
        bucket (str): The name of the S3 bucket.
        folder (str): The folder path in the S3 bucket.
        local_path (str): The local directory to save the downloaded files.
    """
    logging.info(f'Downloading files from S3 bucket {bucket} folder {folder} to local path {local_path}')
    try:
        s3_client = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)

        for obj in response.get('Contents', []):
            key = obj['Key']

            # Skip folders or empty objects
            if key.endswith('/'):
                continue

            # Download the file
            local_file_path = os.path.join(local_path, os.path.basename(key))
            s3_client.download_file(bucket, key, local_file_path)
            logging.info(f'Downloaded s3://{bucket}/{key} to {local_file_path}')
    except Exception as e:
        logging.error(f'Error downloading files from S3: {e}')
        raise

def upload_content_from_fileindexrange_to_s3(brainName):
    """
    Upload the content of the file index range to the S3 bucket.
    
    Args: 
        brainName (str): The name of the brain to associate with the file index range.
    """
    json_file_path = os.path.join(os.environ.get('FILE_INDEX_RANGE'), f"{brainName}.json")
    logging.info(f'Uploading content from file index range to S3 for brain {brainName}')
    s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
    if os.path.exists(json_file_path):
        try:
            s3_key = os.path.join(os.environ.get('S3_MASTER_INDEX_REPO'), f"{brainName}/{os.path.basename(json_file_path)}")
            s3.upload_file(json_file_path, os.environ.get('BUCKET_NAME'), s3_key)
            logging.info(f'Uploaded Json file: {json_file_path} to {s3_key}')
        except Exception as e:
            logging.error(f'Failed to upload {json_file_path}: {e}')
            logging.error(f"Failed to upload {json_file_path}:{str(e)}")

def delete_folder_from_s3(brainName):
    """
    Delete a folder and its contents from the S3 bucket.
    
    Args: 
        brainName (str): The name of the brain associated with the folder to delete.
    """
    logging.info(f'Deleting folder for brain {brainName} from S3')
    try:
        s3 = boto3.resource('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
        bucket = s3.Bucket(os.environ.get('BUCKET_NAME'))
        folder_prefix = f"{os.environ.get('S3_MASTER_DOC_REPO')}/{brainName}/"
        folder_prefix_index = f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{brainName}/"
        bucket.objects.filter(Prefix=folder_prefix).delete()
        bucket.objects.filter(Prefix=folder_prefix_index).delete()
        logging.info(f'Folder for brain {brainName} deleted from S3')
    except Exception as e:
        logging.error(f'Error deleting folder for brain {brainName} from S3: {e}')
        raise

def delete_file_from_s3(brainName, file_name):
    """
    Delete a specific file from the S3 bucket.
    
    Args:
        brainName (str): The name of the brain associated with the file to delete.
        file_name (str): The name of the file to delete.
    """
    logging.info(f'Deleting file {file_name} for brain {brainName} from S3')
    try:
        s3 = boto3.resource('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
        bucket = s3.Bucket(os.environ.get('BUCKET_NAME'))
        file_prefix = f"{os.environ.get('S3_MASTER_DOC_REPO')}/{brainName}/{file_name}"
        bucket.delete_objects(
            Delete={'Objects': [{'Key': file_prefix}]}
        )
        logging.info(f'File {file_name} for brain {brainName} deleted from S3')
    except Exception as e:
        logging.error(f'Error deleting file {file_name} from S3: {e}')
        raise

def rename_s3_folder(old_folder, new_folder):
    """
    Rename a folder in S3 by copying its contents to a new folder and deleting the old folder.

    Args:
        old_folder (str): The old folder path in S3.
        new_folder (str): The new folder path in S3.
    """
    logging.info(f'Renaming folder in S3 from {old_folder} to {new_folder}')
    
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'), aws_secret_access_key=os.environ.get('SECRET_KEY'))
        bucket = os.environ.get('BUCKET_NAME')

        # List objects in the old folder
        response = s3.list_objects_v2(Bucket=bucket, Prefix=old_folder)

        # Copy each object to the new folder
        if 'Contents' in response:
            for obj in response['Contents']:
                old_key = obj['Key']
                new_key = old_key.replace(old_folder, new_folder, 1)

                # Copy object
                s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': old_key}, Key=new_key)
                logging.info(f'Copied {old_key} to {new_key}')
    
    except Exception as e:
        logging.error(f'Error renaming S3 folder from {old_folder} to {new_folder}: {e}')
        raise

def rename_s3_brain_folders(old_brainName, new_brainName):
    """
    Rename the S3 brain folders from old_brainName to new_brainName.

    Args:
        old_brainName (str): The old brain name.
        new_brainName (str): The new brain name.
    """
    # Rename folder in S3 master_doc_repo
    rename_s3_folder(f"{os.environ.get('S3_MASTER_DOC_REPO')}/{old_brainName}/", f"{os.environ.get('S3_MASTER_DOC_REPO')}/{new_brainName}/")

    # Rename folder in S3 master_index_repo
    rename_s3_folder(f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{old_brainName}/", f"{os.environ.get('S3_MASTER_INDEX_REPO')}/{new_brainName}/")

# Additional rules for prompt content handling
# 8. Every Prompt Content passed is preceded with "FileName - >", if you found information for answer from those particular Prompt , at the end of answer return FileName in '[]'.
# 8. convert numbers representing years or monetary amounts into words. For example, 250000 should be written as "two hundred fifty thousand." Dates of birth should be represented in date month_name year format.
# 7. Strictly search only in the file, do not frame your answers based on your knowledge, for answer, strictly search only from the files. Do not add additional information by yourself.
#8. For answering {current_user_input}, you can take reference from {embedd}, if you find {embedd} relevant for answering {current_user_input}.
#9. When asked about "who are {personality_name}", only tell your name, and take reference from information given in prompt, if information not given in prompt, strictly only tell the name, do not write anything else.
