import csv
import os
import chromadb
from dotenv import load_dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

def createVectorDb():
    #load_dotenv()

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print('OpenAI API key not found in environment variables.')
        exit()
        
    data = []
    delimiters = [',', ';', '|', '\t', ':']
    for i in delimiters:
        try:
            loader = CSVLoader(file_path='chatbot_app/files/sessions.csv', encoding='utf-8', source_column='id', csv_args={
                'delimiter': i,
            })
            data = loader.load()
            embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

            # save vectors to chromadb
            conference_id = '12345' # this has to be resolved later 
            persist_directory = 'chatbot_app/vector_db/db_'+conference_id
            Chroma.from_documents(documents=data, embedding=embedding_function, persist_directory=persist_directory)
            break
        except:
            continue