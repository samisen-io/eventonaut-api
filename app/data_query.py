import json
import os
import chromadb
from dotenv import load_dotenv
from langchain.vectorstores import Pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI   
from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain.callbacks import get_openai_callback  
import pinecone

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("OpenAI API key not found in environment variables.")
    exit()
# initialize pinecone
pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment = os.environ.get("PINECONE_API_ENV")
)
# initialize embedding function
embedding_function = OpenAIEmbeddings()

def handler_to_dict(handler):
    # Convert the handler to a dict or another JSON-serializable type
    return handler.__dict__

def retrieve_answer(question, conference_id):
    vectordb = Pinecone.from_existing_index(index_name="eventonaut-events", embedding=embedding_function, namespace='conf-'+conference_id, text_key = 'csv_text')
    chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo-1106', openai_api_key=api_key),
                                                retriever=vectordb.as_retriever(search_kwargs={'k':10}), return_source_documents=True)
    history = []
    return chain({"question": question, "chat_history": history})

def query_document(question, conference_id):
    with get_openai_callback() as cb:
        result = retrieve_answer(question, conference_id)
    usage = json.dumps(cb, default=handler_to_dict, indent=4)
    # retrieve the answer and source documents
    answer = result['answer']
    docs = result['source_documents']
    source_list = []
    for doc in docs:
        metadata = doc.metadata
        source_list.append(metadata['source'])
    data = {
        'answer': answer,
        'source_list': source_list,
        'usage': json.loads(usage)
    }
    json_data = json.dumps(data, indent=4)
    return json_data
    