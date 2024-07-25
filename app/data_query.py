from datetime import datetime
import json
from operator import itemgetter
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain_community.callbacks import get_openai_callback
import pinecone
from app.custom_manager import custom_get_openai_callback
from langchain_core.runnables import RunnablePassthrough
from app.pinecone_operations import get_matching_namespace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import (
    UpstashRedisChatMessageHistory, RedisChatMessageHistory
)
from langchain.memory import ConversationBufferWindowMemory

load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
index_name = os.environ.get("PINECONE_API_INDEX")
upstash_url = os.environ.get("UPSTASH_URL")
upstash_token = os.environ.get("UPSTASH_TOKEN")
if not api_key:
    print("OpenAI API key not found in environment variables.")
    exit()
# initialize pinecone
pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment = os.environ.get("PINECONE_API_ENV")
)
#get redis url
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
redis_url = f"rediss://:{redis_password}@{redis_host}:{redis_port}/1"
# initialize embedding function
embedding_function = OpenAIEmbeddings()

template_for_streaming = """
Eventobot is an assistant that helps attendees query about the event they are attending. The events can be of three types:
1. A conference event (which consists of sessions, speakers, attendees, etc.).
2. A tradeshow event (which consists of exhibitors, attendees, etc.).
3. An "other" type event which is neither of the two.

Instructions for Eventobot:
- If Eventobot doesn't know the answer, it should respond with "I don't know the answer" and suggest exploring other events to get the correct answer.
- Eventobot should provide full details in its responses but should omit any ID details that consist of UUIDs or GUIDs. If someone asks about an ID, it should just say that it cannot provide the ID details.
- Eventobot should use the provided timestamp to answer date and time-related questions.
- Eventobot should answer questions based only on the given context.

Timestamp: {timestamp}

Context: {context}

Current conversation:
{history}

Question: {input}
"""
prompt_for_streaming = ChatPromptTemplate.from_template(template_for_streaming)

template = """
Eventobot is an assistant that helps attendees query about the event they are attending. The events can be of three types:
1. A conference event (which consists of sessions, speakers, attendees, etc.).
2. A tradeshow event (which consists of exhibitors, attendees, etc.).
3. An "other" type event which is neither of the two.

Instructions for Eventobot:
- If Eventobot doesn't know the answer, it should respond with "I don't know the answer" and suggest exploring other events to get the correct answer.
- Eventobot should provide full details in its responses but should omit any ID details that consist of UUIDs or GUIDs. If someone asks about an ID, it should just say that it cannot provide the ID details.
- Eventobot should use the provided timestamp to answer date and time-related questions.
- Eventobot should answer questions based only on the given context.

Timestamp: {timestamp}

Context: {context}

Current conversation:
{chat_history}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def retrieve_answer(question, conference_id):
    namespace = get_matching_namespace(conference_id=conference_id)
    vectordb = Pinecone.from_existing_index(index_name=index_name, embedding=embedding_function, namespace=namespace, text_key = 'csv_text')
    chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.3, model_name='gpt-3.5-turbo-1106', openai_api_key=api_key),
                                                retriever=vectordb.as_retriever(search_kwargs={'k':8}), return_source_documents=True,
                                                combine_docs_chain_kwargs={'prompt':prompt},
                                                get_chat_history = lambda h : h)
    history = []
    return chain({"question": question, "chat_history": history, "timestamp": datetime.now()})

def query_document(question, conference_id, session_id):
    session_id = "chat_"+session_id+conference_id
    with get_openai_callback() as cb:
        result = retrieve_answer_redis(question=question, conference_id=conference_id, session_id=session_id)
    cb_dict = {k: cb.__dict__[k] for k in ('total_cost', 'total_tokens', 'prompt_tokens', 'completion_tokens', 'successful_requests')}
    # convert the dict to a JSON string
    usage = json.dumps(cb_dict, indent=4)
    # retrieve the answer and source documents
    answer = result['answer']
    docs = result['source_documents']
    source_list = []
    for doc in docs:
        metadata = doc.metadata
        if 'source' in metadata:
            source_list.append(metadata['source'])
    data = {
        'answer': answer,
        'source_list': source_list,
        'usage': json.loads(usage)
    }
    json_data = json.dumps(data, indent=4)
    return json_data

def retrieve_answer_redis(question, conference_id, session_id):
    history = RedisChatMessageHistory(
        url=redis_url,
        session_id=session_id,
        ttl=600
    )
    memory = ConversationBufferWindowMemory(
        memory_key = 'chat_history',
        input_key = 'question',
        output_key = 'answer', 
        return_messages = True,
        chat_memory=history,
        k=6
    )
    namespace = get_matching_namespace(conference_id=conference_id)
    vectordb = Pinecone.from_existing_index(index_name=index_name, embedding=embedding_function, namespace=namespace, text_key = 'csv_text')
    chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.3, model_name='gpt-3.5-turbo-1106', openai_api_key=api_key),
                                                retriever=vectordb.as_retriever(search_kwargs={'k':6}), return_source_documents=True,
                                                combine_docs_chain_kwargs={'prompt':prompt},
                                                memory = memory,
                                                get_chat_history = lambda h : h)
    return chain({'question': question, 'timestamp': datetime.now()}, {'configurations': {"session_id": session_id}})

async def retrieve_answer_stream(question, conference_id, session_id):
    namespace = get_matching_namespace(conference_id=conference_id)
    vectordb = Pinecone.from_existing_index(index_name=index_name, embedding=embedding_function, namespace=namespace, text_key = 'csv_text')
    retriever = vectordb.as_retriever(search_kwargs={'k':4})
    model = ChatOpenAI(temperature=0.3, model_name = 'gpt-3.5-turbo-1106', openai_api_key=api_key)
    runnable = prompt_for_streaming | model
    
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        history = RedisChatMessageHistory(
            url=redis_url,
            session_id=session_id,
            ttl=600
        )
        return history
    
    generation_chain = prompt_for_streaming | model
    runnable = (
        {  
            "timestamp": itemgetter("timestamp"),
            "context": itemgetter("input") | retriever,
            "input": itemgetter("input"),
            'history': itemgetter('history'),
        }
        | RunnablePassthrough.assign(output = generation_chain)  
    )
    with_message_history = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    stream = with_message_history.stream({'input': question, 'timestamp': datetime.now()}, {'configurable': {'session_id': session_id}})
    source_list = []
    for chunk in stream:
        if 'context' in chunk:
           for doc in chunk['context']:
               metadata = doc.metadata
               source_list.append(metadata['source'])
           yield source_list
        if 'output' in chunk:
            yield chunk['output'].content
            
    