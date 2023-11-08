import datetime
import os
import csv
import csv
from dotenv import load_dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from app.routers.sessions import get_sessions_by_conference_id

load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print('OpenAI API key not found in environment variables.')
    exit()
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
    file_path = os.path.join(files_folder, 'sessions'+str(conference_id)+'.csv')
    return file_path

def createVectorDb(conference_id):
    file_path = file_path_in_files(conference_id)
    delimiter = find_delimiter(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=delimiter)
        first_row = next(csv_reader)
    # Assuming the first_row contains the column headers, you can access the header of the first column
    if first_row:
        first_column_header = first_row[0]
        print(f"Column header of the first column: {first_column_header}")
    else:
        print("No data found in the CSV file.")
    loader = CSVLoader(file_path=file_path, encoding='utf-8', source_column=first_column_header, csv_args={'delimiter': delimiter,})
    data = loader.load()
    # Define the path to the vector_db folder within the app folder
    vector_db_folder = os.path.join('app', 'vector_db')
    if not os.path.exists(vector_db_folder):
        os.makedirs(vector_db_folder)
    if(len(conference_id)<3):
        conference_id = '0'*(3-len(conference_id))+conference_id        
    vectordb = Chroma.from_documents(documents=data, embedding=embedding_function, persist_directory=vector_db_folder, collection_name=conference_id)
    vectordb.persist()


def write_data_to_csv(conference_id, db):
    file_path = file_path_in_files(conference_id)
    result = get_sessions_by_conference_id(conference_id, db)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'end_time', 'date', 'conference_id', 'start_time', 'description', 'location', 'owner_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for session in result:
            session_dict = session.__dict__
            session_dict.pop('_sa_instance_state', None)
            for field in ['end_time', 'date', 'created_on', 'updated_on', 'start_time']:
                if field in session_dict:
                    if isinstance(session_dict[field], datetime.date):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d")
                    elif isinstance(session_dict[field], datetime.time):
                        session_dict[field] = session_dict[field].strftime("%H:%M:%S")
                    elif isinstance(session_dict[field], datetime.datetime):
                        session_dict[field] = session_dict[field].strftime("%Y-%m-%d %H:%M:%S")
            session_dict.pop('created_on', None)
            session_dict.pop('updated_on', None)
            writer.writerow(session_dict)  
    

