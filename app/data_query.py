import os
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI        

def query_document(question):
    load_dotenv()
    
    app_folder = 'app'

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print('OpenAI API key not found in environment variables.')
        exit()
        
    vector_db_folder = os.path.join(app_folder, 'vector_db')
    if not os.path.exists(vector_db_folder):
        os.makedirs(vector_db_folder)
    
    # save vectors to chromadb
    conference_id = '12345' # this has to resolved later
    persist_directory = os.path.join(vector_db_folder, 'db_'+conference_id)
    
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
    chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo', openai_api_key=api_key), retriever=vectordb.as_retriever())
    history = []
    
    return chain({"question": question, "chat_history": history})["answer"]