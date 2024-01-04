import datetime
import json
import os
import csv
import csv
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from app.crud.conferences_crud import get_conference_by_conference_uuid
from app.crud.speakers_crud import get_speakers_by_conference_id
from app.pinecone_operations import create_namespace
from app.routers.sessions import get_sessions_by_conference_id
import pinecone

load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
index_name = os.environ.get('PINECONE_API_INDEX')
if not api_key:
    print('OpenAI API key not found in environment variables.')
    exit()
# initialize pinecone
pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment = os.environ.get("PINECONE_API_ENV")
)
# initialize embedding function
embedding_function = OpenAIEmbeddings()

def find_delimiter(file_path):
    possible_delimiters = [',', ';', '\t']  # Add more as needed
    with open(file_path, 'r', encoding='utf-8') as file:
        first_line = file.readline()
        for delimiter in possible_delimiters:
            if delimiter in first_line:
                return delimiter
    return ','

def file_path_in_files(conference_id, category):
    app_folder = 'app'
    files_folder = os.path.join(app_folder, 'files')
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)        
    file_path = os.path.join(files_folder, category+'-'+str(conference_id)+'.csv')
    return file_path

def file_path_in_files_csv(conference_id,category):
    file_path = file_path_in_files(conference_id,category)
    # Check if file exists, then delete it
    if os.path.isfile(file_path):
        os.remove(file_path)
    return file_path

def filter_fields(dict_obj, accepted_fields):
    return {k: v for k, v in dict_obj.items() if k in accepted_fields}
    
def write_sessions_to_csv(db,conference_id):
    file_path = file_path_in_files_csv(conference_id, 'sessions')
    result = get_sessions_by_conference_id(conference_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="No sessions found for this conference_id")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name', 'description', 'location', 'date', 'start_time', 'end_time', 'tags', 'speakers', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for session in result:
            session_dict = session.__dict__
            session_dict = filter_fields(session_dict, fieldnames)
            for field in ['end_time', 'date', 'start_time']:
                if field in session_dict:
                    if isinstance(session_dict[field], datetime.date):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d")
                    elif isinstance(session_dict[field], datetime.time):
                        session_dict[field] = session_dict[field].strftime("%H:%M:%S")
                    elif isinstance(session_dict[field], datetime.datetime):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d %H:%M:%S")
            session_dict['type'] = 'session'
            writer.writerow(session_dict)
            
def write_speakers_to_csv(db, conference_id):
    file_path = file_path_in_files_csv(conference_id,'speakers')
    result = get_speakers_by_conference_id(db, conference_id)
    if not result:
        raise HTTPException(status_code=404, detail="No speakers found for this conference_id")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name','conference_id','title','bio', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for speaker in result:
            speaker_dict = speaker.__dict__
            speaker_dict = filter_fields(speaker_dict, fieldnames)
            speaker_dict['type'] = 'speaker'
            writer.writerow(speaker_dict)

def write_events_to_csv(db, conference_id):
    file_path = file_path_in_files_csv(conference_id,'events')
    result = get_conference_by_conference_uuid(db, conference_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conference not found")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name', 'description', 'location', 'start_date', 'end_date', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        conference_dict = result.__dict__
        conference_dict = filter_fields(conference_dict, fieldnames)
        conference_dict['type'] = 'event/conference'
        writer.writerow(conference_dict)

# def add_documents(conference_id,category):
#     # get the file path
#     file_path = file_path_in_files(conference_id,category)
#     # find the delimiter
#     delimiter = find_delimiter(file_path)
#     # split the csv file into chunks
#     loader = CSVLoader(file_path = file_path, encoding='utf-8',source_column = 'uuid',csv_args = {'delimiter': delimiter})
#     data = loader.load()
#     # get the pineone index
#     namespace = "conf-"+str(conference_id)
#     index = pinecone.Index(index_name)
#     vectorstore = Pinecone(index, embedding=embedding_function, text_key = 'csv_text', namespace = namespace)
#     vectorstore.add_documents(documents = data)
#     # Delete the file
#     # try:
#     #     os.remove(file_path)
#     # except OSError as e:
#     #     print(f"Error: {file_path} : {e.strerror}")
#     return {"namespace":namespace}

def add_documents(namespace,conference_id,category):
    # get the file path
    file_path = file_path_in_files(conference_id,category)
    # find the delimiter
    delimiter = find_delimiter(file_path)
    # split the csv file into chunks
    loader = CSVLoader(file_path = file_path, encoding='utf-8',source_column = 'uuid',csv_args = {'delimiter': delimiter})
    data = loader.load()
    # get the pineone index
    index = pinecone.Index(index_name)
    vectorstore = Pinecone(index, embedding=embedding_function, text_key = 'csv_text', namespace = namespace)
    vectorstore.add_documents(documents = data)
    # Delete the file
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error: {file_path} : {e.strerror}")
    return {"namespace":namespace}