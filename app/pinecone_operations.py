import os
from fastapi import HTTPException
import pinecone

# initialize pinecone
pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment = os.environ.get("PINECONE_API_ENV")
)

def delete_vector_db(conference_id):
    index_name = "sessions-"+str(conference_id)
    if index_name in pinecone.list_indexes():
        try:
            pinecone.delete_index(index_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Unable to delete index: " + str(e))
        return {'index_name': index_name, 'status': 'deleted'}
    
    else:
        return {'index_name': index_name, 'status': 'not found'}