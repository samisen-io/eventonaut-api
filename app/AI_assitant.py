from openai import OpenAI

client = OpenAI()

def create_assistant(name: str):
    global client
    assistant = client.beta.assistants.create(
        name=name,
        model="gpt-4-1106-preview",
        instructions="You are conference assitant. You can help users with their queries related to the sessions of the conference to build their agenda/schedule."
    )
    return assistant


def file_upload(file):
    global client
    uploaded_file = client.files.create(file=file)
    return uploaded_file

def create_thread():
    global client
    return client.beta.threads.create()