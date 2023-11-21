import os
import time
from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI


load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print('OpenAI API key not found in environment variables.')
    exit()
    
client = OpenAI()

def create_message(thread_id, question, file_id):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role = "user",
        content = question,
        file_ids = file_id
    )
    return message

def create_run(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = assistant_id,
        instructions = """User is an attendee to a conference, and wants to know about the conference. 
        Please be a helpful assistant and answer the user's question.
        And answer them only in text format."""
    )
    return run

def check_run_status_and_retrieve(thread_id, run):
    while(True):
        if(run.status == 'failed'):
            raise HTTPException(status_code=400, detail="OpenAI API request failed")
        elif(run.status == 'expired'):
            raise HTTPException(status_code=410, detail="OpenAI API request expired")
        elif(run.status == 'cancelled'):
            raise HTTPException(status_code=422, detail="OpenAI API request was cancelled")
        elif(run.status == 'completed'):
            break
        else:
            run = client.beta.threads.runs.retrieve(
                thread_id = thread_id,
                run_id = run.id
            )
        time.sleep(1)

def query_document(question,assistant_id,thread_id,file_id):
    # create message
    message = create_message(thread_id, question, file_id)
    # run the assistant
    run = create_run(thread_id, assistant_id)
    # check the run status and retrieve the assistant's response
    run = check_run_status_and_retrieve(thread_id, run)
    # display the assistant's response
    messages = client.beta.threads.messages.list(
        thread_id = thread_id
    )
    data = messages.data
    data_list = list(data)
    if not data_list or not data_list[0].content or not data_list[0].content[0].text:
        raise Exception("No messages found in the thread or the first message doesn't have any content or text")
    return data_list[0].content[0].text.value