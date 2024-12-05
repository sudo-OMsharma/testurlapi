import os
import logging
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import fitz
from nltk.tokenize import word_tokenize
from docx import Document

def get_pdf_text(pdf_path):
    """
    Extract text from a PDF file, including text from images using Tesseract.
    
    Args: 
        pdf_path (str): The path to the PDF file.
        
    Returns:
        str: The extracted text from the PDF.
    """
    logging.info(f'Extracting text from PDF {pdf_path}')
    try:
        text = ""
        pdf_document = fitz.open(pdf_path)
        image_counter = 0

        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]

            # Check if the page contains images and image counter is less than 5
            if page.get_images(full=True) and image_counter < 5:
                # Extract text from images using Tesseract
                for img_info in page.get_images(full=True):
                    if image_counter >= 5:
                        break
                    image = page.get_pixmap()
                    img = Image.frombytes("RGB", [image.width, image.height], image.samples)
                    text += pytesseract.image_to_string(img) + ' '
                    image_counter += 1
            else:
                # Extract regular text content using PyMuPDF
                text += page.get_text() + ' '

        pdf_document.close()
        logging.info(f'Text extracted from PDF {pdf_path}')
        return text
    except Exception as e:
        logging.error(f'Error extracting text from PDF {pdf_path}: {e}')
        raise

def get_txtfile_text(text_doc_path):
    """
    Extract text from a .txt file.
    
    Args: 
        text_doc_path (str): The path to the .txt file.
        
    Returns:
        tuple: The extracted text and a boolean flag indicating whether there was an error.
    """
    try:
        with open(text_doc_path, 'r', encoding='utf-8') as file:
            logging.info('Text file read successfully')
            return file.read(), False # Return text and a flag indicating no error
    except UnicodeDecodeError:
        logging.error('Error reading text file: Unsupported content')
        return "File has unsupported content in it", True

def get_docxfile_text(docx_file):
    """
    Extract text from a .docx file.
    
    Args:
        docx_file (str): The path to the .docx file.
    
    Returns: 
        str: The extracted text from the .docx file.
    """
    logging.info(f'Reading DOCX file {docx_file}')
    try:
        doc = Document(docx_file)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        logging.info(f'DOCX file read successfully')
        return text
    except Exception as e:
        logging.error(f'Error reading DOCX file {docx_file}: {e}')
        raise

# Creates text corpus of all documents
def load_all_text(source_fold):
    """
    Create a text corpus from all documents in a source folder.
    
    Args: 
        source_fold (str): The path to the source folder.
    
    Returns: 
        tuple: The concatenated text from all documents and a boolean flag indicating whether there was an error.
    """
    logging.info(f'Loading all text from folder {source_fold}')
    filedata = ""
    error_flag = False
    try:
        doc_list = os.listdir(source_fold)
        for file_name in doc_list:
            if file_name.endswith('.pdf'):
                filedata = get_pdf_text(os.path.join(source_fold, file_name))
            elif file_name.endswith('.txt'):
                filedata, flag = get_txtfile_text(os.path.join(source_fold, file_name))
                if flag:
                    return filedata, True
            elif file_name.endswith('.docx'):
                filedata = get_docxfile_text(os.path.join(source_fold, file_name))

        if not filedata or filedata.isspace():
            error_flag = True   

        logging.info(f'All text loaded from folder {source_fold} with error flag {error_flag}')
        return filedata, error_flag
    except Exception as e:
        logging.error(f'Error loading all text from folder {source_fold}: {e}')
        raise

def split_text(input_text, words_per_chunk):
    """
    Split text into chunks of a specified number of words.
    
    Args:  
        input_text (str): The text to be split.
        words_per_chunk (int): The number of words per chunk.
    
    Returns: 
        list: A list of text chunks.
    """
    logging.info(f'Splitting text into chunks of {words_per_chunk} words')
    try:
        words = word_tokenize(input_text)
        chunks = [words[i:i + words_per_chunk] for i in range(0, len(words), words_per_chunk)]
        logging.info(f'Text successfully split into {len(chunks)} chunks')
        return chunks
    except Exception as e:
        logging.error(f'Error splitting text into chunks: {e}')
        raise

def search_file_name_from_index(dict, key):
    """
    Search for a file name in the index dictionary using a key.
    
    Args: 
        dict (dict): The dictionary containing file index ranges.
        key (int): The key to search for.
        
    Returns:
        str: The file name if found, otherwise None.
    """
    logging.info(f'Searching file name from index for key {key}')
    try:
        for x in dict:
            if key in range(dict[x][0], dict[x][1]+1):
                return x
    except Exception as e:
        logging.error(f'Error searching file name from index: {e}')
        raise
