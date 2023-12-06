import datetime
import json
import os
import csv
import csv
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from app.routers.sessions import get_sessions_by_conference_id
import pinecone

load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
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

def file_path_in_files(conference_id):
    app_folder = 'app'
    files_folder = os.path.join(app_folder, 'files')
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)        
    file_path = os.path.join(files_folder, 'sessions-'+str(conference_id)+'.csv')
    return file_path

def file_path_in_files_csv(conference_id):
    file_path = file_path_in_files(conference_id)
    # Check if file exists, then delete it
    if os.path.isfile(file_path):
        os.remove(file_path)
    return file_path

def file_path_in_files_json(conference_id):
    app_folder = 'app'
    files_folder = os.path.join(app_folder, 'files')
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)        
    file_path = os.path.join(files_folder, 'sessions-'+str(conference_id)+'.json')
    # Check if file exists, then delete it
    if os.path.isfile(file_path):
        os.remove(file_path)
    return file_path

def write_data_to_json(conference_id, db):
    file_path = file_path_in_files_json(conference_id)
    result = get_sessions_by_conference_id(conference_id, db)    
    json_result = json.dumps([{
        key: value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime.datetime) 
             else value.strftime("%H:%M:%S") if isinstance(value, datetime.time)
             else value.strftime("%Y-%m-%d") if isinstance(value, datetime.date)
             else value 
        for key, value in row.__dict__.items() 
        if key != '_sa_instance_state' and key not in ['id', 'created_on', 'conference_id', 'updated_on', 'owner_id']
    } for row in result])
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json.loads(json_result), f, indent=4)
    
def write_data_to_csv(conference_id, db):
    file_path = file_path_in_files_csv(conference_id)
    result = get_sessions_by_conference_id(conference_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="No sessions found for this conference_id")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name', 'description', 'location', 'date', 'start_time', 'end_time', 'tags', 'speakers']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for session in result:
            session_dict = session.__dict__
            # session_dict.pop('_sa_instance_state', None)
            for field in ['end_time', 'date', 'created_on', 'updated_on', 'start_time']:
                if field in session_dict:
                    if isinstance(session_dict[field], datetime.date):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d")
                    elif isinstance(session_dict[field], datetime.time):
                        session_dict[field] = session_dict[field].strftime("%H:%M:%S")
                    elif isinstance(session_dict[field], datetime.datetime):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d %H:%M:%S")
            discard = ['id', 'conference_id', 'owner_id', 'created_on', 'updated_on','_sa_instance_state']
            for field in discard:
                session_dict.pop(field, None)
            writer.writerow(session_dict)  
            
def create_vector_db(conference_id):
    # get the file path
    file_path = file_path_in_files(conference_id)
    # find the delimiter
    delimiter = find_delimiter(file_path)
    # split the csv file into chunks
    loader = CSVLoader(file_path = file_path, encoding='utf-8',source_column = 'uuid',csv_args = {'delimiter': delimiter})
    data = loader.load()
    # create pinecone index
    index_name = "sessions-"+str(conference_id)
    try:
        pinecone.create_index(name = index_name, dimension=1536, metric = "cosine", shards=1)
    except Exception as e:
        raise HTTPException(status_code=409, detail="Unable to create index: " + str(e))
    # upload the data to pinecone
    try:
        Pinecone.from_documents(documents = data, index_name=index_name, embedding=embedding_function)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to upload documents: " + str(e))
    return index_name
    
