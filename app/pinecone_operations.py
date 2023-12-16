import os
from fastapi import HTTPException
import pinecone

# initialize pinecone
pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment = os.environ.get("PINECONE_API_ENV")
)
index_name = os.environ.get("PINECONE_API_INDEX")

def create_vector_db(name):
    index_name = name
    try:
        pinecone.create_index(name = index_name, dimension=1536, metric = "cosine", shards=1)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    os.environ.update("PINECONE_API_INDEX", index_name)
    return {"index_name": index_name}

def delete_vector_db():
    # index_name = index_name
    if index_name in pinecone.list_indexes():
        try:
            pinecone.delete_index(index_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Unable to delete index: " + str(e))
        return {'index_name': index_name, 'status': 'deleted'}
    
    else:
        return {'index_name': index_name, 'status': 'not found'}
    
def delete_namespace(conference_id):
    # index_name = index_name
    index = pinecone.Index(index_name)
    if index_name in pinecone.list_indexes():
        namespace = 'conf-'+str(conference_id)
        # check if the namespace exists
        try:
            index.delete(delete_all=True, namespace=namespace)
            return {'namespace': namespace, 'status': 'deleted'}
        except:
            return {'namespace': namespace, 'status': 'not found'}