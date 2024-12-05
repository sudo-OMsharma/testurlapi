# Multi Brain PersonaAI is a custom llm platform where multiple custom knowledge llm bots can be prepared with user’s access to ingest or delete data. And the user can ask questions in natural language and get answers in the same from the ingested documents.
Document Upload APIs For AHL , Twin , Email , Slack Integration

All Data Is Maintained in S3 Bucketi

## Installation
Install all dependencies from requirements.txt

bash
 pip3 install -r requirements.txt

    
You will need to install the 'punkt' Module of Nltk Library too,
Simply Login Your Terminal with Python

bash
```
python3 
>> import nltk
>> nltk.download('punkt')
>> exit()
```
You will also need to install the 'vader_lexicon' Module of Nltk Library too,
Simply Login Your Terminal with Python

bash
```
python3
>> import Nltk
>> nltk.download('vader_lexicon')
>> exit()
```

You will need to install the 'tesseract-ocr' Module of Tesseract Library too,

bash
 sudo apt purge tesseract* libtesseract*
 sudo apt autoremove --purge

 sudo apt install tesseract-ocr -y


You will need to create a folder 'static'
bash
  mkdir static
  
  
## Deployment

## Create Folders As Following If Not Present - <br>
1 . connectionindex <br>
2 . fileindexrange <br>
3 . tempcreatedindex <br>
4 . tempcreateddoc <br>

You need to define below two paramters as per your requirement, <br>
To get best answers use the gpt models as guided below in .env file <br>

OPENAI_MODEL=gpt-4  <br>
OPENAI_MODEL_1=gpt-3.5-turbo <br>


To migrate when first starting the application-
bash
```
	python3 manage.py migrate
```

To run this project - 
bash
  ```
	python3 manage.py runserver
```



## Log File -
- Make a folder named `logs`: 
The below files are generated inside this folder

    - log_info.log
    - log_error.log 


## API Reference

#### createbrains API 

#### Description 

This API allows users to create a new brain (Folder in S3) by providing a unique brain name and a personality name. The brain is created in the S3 bucket and the file index range is saved.

```http
  POST /createbrains/start
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `brainName` | `string` | **Required** The unique identifier for the new brain
 `personality_name`| `string` | **Required** The personality name associated with the brain. Should only contain alphabetic characters and spaces.

#### upload API 

#### Description 

This API allows users to upload files to a specific brain. The files are processed, their content is converted to text, and embeddings are created or appended for the brain.


```http
  POST /upload/start
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `brainName` | `string` | **Required** The unique identifier for the brain
 `file`| `file` | **Required** The files to be uploaded. Supports .txt, .pdf, and .docx formats. Multiple files can be uploaded at once.


#### chat API 

#### Description 

This API allows users to interact with the custom LLM bots by asking questions in natural language and getting responses based on the ingested documents.

```http
  POST /chat/start
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `llm` | `string` | **Required** The language model to be used. Should be 'openai'.
 `brainName`| `string` | **Required** The identifier for the specific folder (brain)
 `current_user_quetsion` | `string` | **Required** The question being asked by the user 
 `word_limit`| `int` | **Required** The maximum number of words in the response|
 `previous_question`| `string` | The previous question asked in the session.
 `previous_answer`| `string` | The previous answer provided in the session.


#### deletefile API 

#### Description 

This API allows users to delete specific files from a given brain. The embeddings and indexes associated with these files are also removed.


```http
  POST /deletefile/start
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `brainName` | `string` | **Required** The unique identifier for the brain
 `file_names`| `file` | **Required** file that needs to be deleted from the specified brain. Multiple file can be deleted at once.

#### deletebrain API 

#### Description 

This API deletes a specified brain from both the runtime memory and the S3 storage system.


```http
  POST /deletebrain/start
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `brainName` | `string` | **Required** The unique identifier for the brain

#### deleteram API 

#### Description 

This API deletes a specified brain's embedding data from runtime memory. If no brain name is provided, it clears all brain indexes from memory.


```http
  POST /deletebrain/start
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `brainName` | `string` | The unique identifier for the brain

#### membrains API 

#### Description 

This API retrieves the current state of the MASTER_EMBEDDING_ARRAY from memory, displaying the runtime embeddings of all brains. (Shows number of brains loaded in the memory)


```http
  GET /membrains/start
```

 This api does not require any Parameters. 