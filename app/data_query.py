import os
import chromadb
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI   
from langchain.embeddings.openai import OpenAIEmbeddings     

load_dotenv()
app_folder = 'app'
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print('OpenAI API key not found in environment variables.')
    exit()
embedding_function = OpenAIEmbeddings()


def query_document(question, conference_id):           
    vector_db_folder = os.path.join(app_folder, 'vector_db')
    chromadb.PersistentClient(path=vector_db_folder)
    if(len(conference_id)<3):
        conference_id = '0'*(3-len(conference_id))+conference_id
    vectordb = Chroma(collection_name = conference_id, embedding_function = embedding_function, persist_directory = vector_db_folder)
    chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo', openai_api_key=api_key),
                                                  retriever=vectordb.as_retriever())
    history = []
    return chain({"question": question, "chat_history": history})["answer"]