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
    
def write_sessions_to_csv(db,conference_id):
    file_path = file_path_in_files_csv(conference_id, 'sessions')
    result = get_sessions_by_conference_id(conference_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="No sessions found for this conference_id")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name', 'description', 'location', 'date', 'start_time', 'end_time', 'tags', 'speakers']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for session in result:
            session_dict = session.__dict__
            discard = ['id', 'conference_id', 'owner_id', 'created_on', 'updated_on','_sa_instance_state']
            for field in discard:
                session_dict.pop(field, None)
            for field in ['end_time', 'date', 'created_on', 'updated_on', 'start_time']:
                if field in session_dict:
                    if isinstance(session_dict[field], datetime.date):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d")
                    elif isinstance(session_dict[field], datetime.time):
                        session_dict[field] = session_dict[field].strftime("%H:%M:%S")
                    elif isinstance(session_dict[field], datetime.datetime):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow(session_dict)  
            
def write_speakers_to_csv(db, conference_id):
    file_path = file_path_in_files_csv(conference_id,'speakers')
    result = get_speakers_by_conference_id(db, conference_id)
    if not result:
        raise HTTPException(status_code=404, detail="No speakers found for this conference_id")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        filednames = ['uuid','name','conference_id','title','bio']
        writer = csv.DictWriter(csvfile, fieldnames=filednames)
        writer.writeheader()
        for speaker in result:
            speaker_dict = speaker.__dict__
            discard = ['id', 'created_on', 'updated_on','_sa_instance_state','profile_image_url']
            for field in discard:
                speaker_dict.pop(field, None)
            writer.writerow(speaker_dict)

def write_events_to_csv(db, conference_id):
    file_path = file_path_in_files_csv(conference_id,'events')
    result = get_conference_by_conference_uuid(db, conference_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conference not found")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name', 'description', 'location', 'start_date', 'end_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        conference_dict = result.__dict__
        discard = ['id', 'created_on', 'updated_on','_sa_instance_state','owner_id','conferenece_logo','assistant_id','code','timezone','registration_link','client_id', 'conference_logo', 'information_guide']
        for field in discard:
            conference_dict.pop(field, None)
        writer.writerow(conference_dict)  

def add_documents(conference_id,category):
    # get the file path
    file_path = file_path_in_files(conference_id,category)
    # find the delimiter
    delimiter = find_delimiter(file_path)
    # split the csv file into chunks
    loader = CSVLoader(file_path = file_path, encoding='utf-8',source_column = 'uuid',csv_args = {'delimiter': delimiter})
    data = loader.load()
    # get the pineone index
    namespace = "conf-"+str(conference_id)
    index = pinecone.Index(index_name)
    vectorstore = Pinecone(index, embedding=embedding_function, text_key = 'csv_text', namespace = namespace)
    vectorstore.add_documents(documents = data)
    # Delete the file
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error: {file_path} : {e.strerror}")
    return {"namespace":namespace}