import os
import csv
from dotenv import load_dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

def find_delimiter(file_path, possible_delimiters):
    with open(file_path, 'r', encoding='utf-8') as file:
        first_line = file.readline()
        for delimiter in possible_delimiters:
            if delimiter in first_line:
                return delimiter
    return ','  # Default to comma if none of the possible delimiters are found

def createVectorDb(conference_id):
    load_dotenv()

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print('OpenAI API key not found in environment variables.')
        exit()
    
    app_folder = 'app'

    # # Define the path to the vector_db folder within the app folder
    files_folder = os.path.join(app_folder, 'files')
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)
        
    file_path = os.path.join(files_folder, 'sessions'+conference_id+'.csv')

    # List of possible delimiters
    possible_delimiters = [',', ';', '\t']  # Add more as needed

    # Find the delimiter
    delimiter = find_delimiter(file_path, possible_delimiters)

    # Read the CSV file using the determined delimiter
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=delimiter)
        first_row = next(csv_reader)  # Get the first row

    # Assuming the first_row contains the column headers, you can access the header of the first column
    if first_row:
        first_column_header = first_row[0]
        print(f"Column header of the first column: {first_column_header}")
    else:
        print("No data found in the CSV file.")
        
    loader = CSVLoader(file_path=file_path, encoding='utf-8', source_column=first_column_header, csv_args={
                'delimiter': delimiter,
            })
    
    data = loader.load()
        
    embedding_function = OpenAIEmbeddings()

    # Define the path to the vector_db folder within the app folder
    vector_db_folder = os.path.join(app_folder, 'vector_db')
    if not os.path.exists(vector_db_folder):
        os.makedirs(vector_db_folder)
    
    # save vectors to chromadb
    # conference_id = '12345' # this has to be resolved later
    # persist_directory = os.path.join(vector_db_folder, 'db_'+conference_id)
    # if not os.path.exists(persist_directory):
    #     os.makedirs(persist_directory)
    vectordb = Chroma.from_documents(documents=data, embedding=embedding_function, persist_directory=vector_db_folder, collection_name=conference_id)
    vectordb.persist()

        
        