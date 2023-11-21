import os
import chromadb
from fastapi import HTTPException
from langchain.vectorstores import Chroma

vector_db_folder = os.path.join('app', 'vector_db')
if not os.path.exists(vector_db_folder):
        os.makedirs(vector_db_folder)

def delete_collection(conference_id):        
    if(len(conference_id)<3):
        conference_id = '0'*(3-len(conference_id))+conference_id    
    client = chromadb.PersistentClient(persist_directory = vector_db_folder)
    if conference_id not in client.list_collections():
        HTTPException(status_code=400, detail="Conference id not found")
    vectordb = Chroma(collection_name = conference_id, persist_directory = vector_db_folder)
    id_list = get_id_list_from_collection(conference_id)
    if id_list:
        vectordb.delete(id_list)
        vectordb.delete_collection()
    
def get_id_list_from_collection(conference_id):
    if(len(conference_id)<3):
        conference_id = '0'*(3-len(conference_id))+conference_id
    vectordb = Chroma(collection_name = conference_id, persist_directory = vector_db_folder)
    collection = vectordb.get()
    id_list = collection.get('ids')
    return id_list