import datetime
import logging
import mimetypes
import os
import csv
import csv
import tempfile
from urllib.parse import urlparse
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import requests
from app.crud.conferences_crud import get_conference_by_conference_uuid
from app.crud.event_documents_crud import get_event_documents_by_conference_id
from app.crud.exhibitor_crud import get_exhibitors
from app.crud.exhibitor_documents_crud import get_exhibitor_documents_by_exhibitor_id
from app.crud.session_document_crud import get_session_document_by_conference_id
from app.crud.speakers_crud import get_speakers_by_session_uuid
from app.file_type_handler import add_csv_documents, add_pdf_document, add_txt_documents, read_the_structured_file
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
            speakers = get_speakers_by_session_uuid(db, session_dict['uuid'])
            speaker_names = []
            for speaker in speakers:
                speaker_names.append(speaker.name)
            session_dict['speakers'] = speaker_names
            writer.writerow(session_dict)
            
def write_speakers_to_csv(db, conference_id):
    file_path = file_path_in_files_csv(conference_id,'speakers')
    result = get_sessions_by_conference_id(conference_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="No sessions found for this conference_id")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name','conference_id','title','bio', 'type', 'conferene_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for session in result:
            speakers = get_speakers_by_session_uuid(db, session.uuid)
            for speaker in speakers:
                speaker_dict = speaker.__dict__
                speaker_dict = filter_fields(speaker_dict, fieldnames)
                speaker_dict['type'] = 'speaker' 
                speaker_dict['conferene_name'] = session.name
                writer.writerow(speaker_dict)

def write_events_to_csv(db, conference_id):
    file_path = file_path_in_files_csv(conference_id,'events')
    result = get_conference_by_conference_uuid(db, conference_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conference not found")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        dict_obj = result.__dict__
        venue_fields = ['name','location','address']
        venue = dict_obj['venue'].__dict__
        venue = filter_fields(venue, venue_fields)
        venue = {'venue_' + key: value for key, value in venue.items()}
        venue_fields = ['venue_' + field for field in venue_fields]
        fieldnames = ['uuid','name', 'description', 'location', 'start_date', 'end_date', 'type', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames + venue_fields)
        conference_dict = result.__dict__
        conference_dict = filter_fields(conference_dict, fieldnames)
        conference_dict['type'] = 'event/conference/trade_show'
        merged_dict = {**conference_dict, **venue}
        writer.writeheader()
        writer.writerow(merged_dict)
        
def write_exhibitors_to_csv(db, conference_id):
    file_path = file_path_in_files_csv(conference_id,'exhibitors')
    result = get_conference_by_conference_uuid(db, conference_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conference not found")
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['uuid','name','address','about', 'contact_email', 'booth_number', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for exhibitor in result.exhibitors:
            exhibitor_dict = exhibitor.__dict__
            exhibitor_dict = filter_fields(exhibitor_dict, fieldnames)
            exhibitor_dict['type'] = 'exhibitor'
            writer.writerow(exhibitor_dict)

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

def process_document(document, namespace):
    url = document.document_url
    parsed_url = urlparse(url)
    _, extension = os.path.splitext(parsed_url.path)
    if extension is None:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        files_folder = os.path.join('app', 'files')
        if not os.path.exists(files_folder):
            os.makedirs(files_folder) 
        file_path = os.path.join(files_folder, str(document.uuid)+extension)
        with open(file_path, 'wb') as fp:
            for chunk in response.iter_content(chunk_size = 8192):
                if chunk:
                    fp.write(chunk)
        if extension == '.pdf':
            add_pdf_document(namespace, file_path)
        elif extension in ['.csv', '.xlsx']:
            reader, delimiter = read_the_structured_file(file_path)
            with tempfile.NamedTemporaryFile(mode='w+t', delete=False, encoding='utf-8') as temp:
                writer = csv.DictWriter(temp, fieldnames=reader.fieldnames)
                writer.writeheader()
                for row in reader:
                    writer.writerow(row)
            add_csv_documents(namespace, temp.name, delimiter)
            os.remove(file_path)
        elif extension == '.txt':
            add_txt_documents(namespace, file_path)
        else:
            os.remove(file_path)
    return True
            
def write_session_docs(db, conference_id, namespace):
    conference = get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    session_documents = get_session_document_by_conference_id(db, conference.id)
    status = None
    for session_document in session_documents:
        status = process_document(session_document, namespace)
    if status:
        logging.info(f"Session documents added: {len(session_documents)}")

def write_event_docs(db, conference_id, namespace):
    print(f"Writing event documents {namespace}")
    conference = get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    event_docs = get_event_documents_by_conference_id(db, conference.id)
    status = None
    for event_doc in event_docs:
        status = process_document(event_doc, namespace)
    if status:
        logging.info(f"Event documents added")

def write_exhibitor_docs(db, conference_id, namespace):
    conference = get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    exhibitors = get_exhibitors(db, conference.id)
    if not exhibitors:
        raise HTTPException(status_code=404, detail="No exhibitors found for this conference_id")
    status = None
    for exhibitor in exhibitors:
        exhibitor_docs = get_exhibitor_documents_by_exhibitor_id(db, exhibitor.id)
        if exhibitor_docs:
            for exhibitor_doc in exhibitor_docs:
                status = process_document(exhibitor_doc, namespace)
    if status:
        logging.info(f"Exhibitor documents added")
                    
                    
                           

        