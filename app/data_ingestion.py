import os
from dotenv import load_dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings


def createVectorDb():
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
        
    file_path = os.path.join(files_folder, 'sessions.csv')
    
    data = None
    flag = 0
    delimiters = [',', ';', '|', '\t', ':']
    for i in delimiters:
        try:
            loader = CSVLoader(file_path=file_path, encoding='utf-8', source_column='id', csv_args={
                'delimiter': i,
            })
            data = loader.load()
            flag = 1
            break
        
        except:
            continue
    
    if flag == 0:
        print("No delimiter found")
        exit()
        
    embedding_function = OpenAIEmbeddings()

    # Define the path to the vector_db folder within the app folder
    vector_db_folder = os.path.join(app_folder, 'vector_db')
    if not os.path.exists(vector_db_folder):
        os.makedirs(vector_db_folder)
    
    # save vectors to chromadb
    conference_id = '12345' # this has to be resolved later
    persist_directory = os.path.join(vector_db_folder, 'db_'+conference_id)
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
            
    vectordb = Chroma.from_documents(documents=data, embedding=embedding_function, persist_directory=persist_directory)
    vectordb.persist()

        
        