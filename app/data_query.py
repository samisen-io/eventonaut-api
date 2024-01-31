import json
from operator import itemgetter
import os
from dotenv import load_dotenv
from langchain.vectorstores import Pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI   
from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain.callbacks import get_openai_callback  
import pinecone
from app.custom_manager import custom_get_openai_callback
from app.pinecone_operations import get_matching_namespace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
index_name = os.environ.get("PINECONE_API_INDEX")
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

def retrieve_answer(question, conference_id):
    namespace = get_matching_namespace(conference_id=conference_id)
    vectordb = Pinecone.from_existing_index(index_name=index_name, embedding=embedding_function, namespace=namespace, text_key = 'csv_text')
    chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.3, model_name='gpt-3.5-turbo-1106', openai_api_key=api_key),
                                                retriever=vectordb.as_retriever(search_kwargs={'k':10}), return_source_documents=True)
    history = []
    return chain({"question": question, "chat_history": history})

def query_document(question, conference_id):
    with get_openai_callback() as cb:
        result = retrieve_answer(question, conference_id)
    cb_dict = {k: cb.__dict__[k] for k in ('total_cost', 'total_tokens', 'prompt_tokens', 'completion_tokens', 'successful_requests')}
    # convert the dict to a JSON string
    usage = json.dumps(cb_dict, indent=4)
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

async def retrieve_answer_stream(question, conference_id):
    namespace = get_matching_namespace(conference_id=conference_id)
    vectordb = Pinecone.from_existing_index(index_name=index_name, embedding=embedding_function, namespace=namespace, text_key = 'csv_text')
    retriever=vectordb.as_retriever(search_kwargs={'k': 8})
    template = """
    You are a helpful assistant for a conference. \
    The conferene is contains speakers and sessions on a variety of topics. \
    You are helping a participant to query about the conference. \
    If you dont know the answer, you can say "I don't know" and suggest to access the other conferences/events to get the correct answers. \
    and answer the question based only on the following context : \
    {context}

    current conversation: 
    {history}

    Question: {input}
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo-1106', openai_api_key=api_key)
    docs = retriever.get_relevant_documents(question)
    source_list = []
    for doc in docs:
        metadata = doc.metadata
        source_list.append(metadata['source'])
        
    with custom_get_openai_callback() as handler:
        event_chain = (
            {
                "context": itemgetter("input") | retriever,
                "input": itemgetter("input"),
                "history": itemgetter("history"),
            }
            | prompt
            | model
        )
        yield source_list
        for chunk in event_chain.stream({'input': question, 'history': []}):
            yield chunk.content
    
    