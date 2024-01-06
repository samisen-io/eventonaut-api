import json
import os
import re
from fastapi import HTTPException
import pinecone

# initialize pinecone
pinecone.init(
    api_key=os.environ.get("PINECONE_API_KEY"),
    environment = os.environ.get("PINECONE_API_ENV")
)
index_name = os.environ.get("PINECONE_API_INDEX")

def increment_number(s):
    match = re.match(r'(\d+)(.*)', s)
    if match:
        number, rest = match.groups()
        return str(int(number) + 1) + rest
    else:
        return '1' + s
    
def get_matching_namespace(conference_id):
    namespaces = get_namespaces()
    for namespace in namespaces:
        if str(conference_id) in namespace:
            return namespace
    return None

def get_namespaces():
    index = pinecone.Index(index_name)
    data = index.describe_index_stats()
    namespaces = list(data['namespaces'].keys())
    return namespaces

def create_namespace(conference_id):
    namespaces = get_namespaces()
    incremented_string = conference_id
    # Iterate over each string in the list
    for s in namespaces:
        # If the input string is a substring of the current string, increment the number in front of the string
        if conference_id in s:
            incremented_string = increment_number(s)
            break  # Stop after finding the first match
    return incremented_string

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
    index = pinecone.Index(index_name)
    print('get_namespaces')
    namespaces = get_namespaces()
    print('after get_namespaces')
    # check if the conference_id is a substring of any namespace
    for namespace in namespaces:
        if str(conference_id) in namespace:
            try:
                index.delete(delete_all=True, namespace=namespace)
                return {'namespace': namespace, 'status': 'deleted'}
            except:
                return {'namespace': namespace, 'status': 'not found'}
    return {'status': 'conference_id not in any namespace'}
            
def arranging_ouput_object(json_data):
    data = json.loads(json_data)
    speakers = []
    sessions = []
    events = []
    # Iterate over the dictionaries in the data
    for obj in data:
        # Rename 'uuid' to 'id'
        obj['id'] = obj.pop('uuid')
        if obj['id'].startswith('spk'):
            speakers.append(obj)
        elif obj['id'].startswith('ses'):
            sessions.append(obj)
        elif obj['id'].startswith('evt'):
            events.append(obj)    
    
    data_dict = {
        'speakers': speakers,
        'sessions': sessions,
        'events': events
    }
    # Convert the dictionary to a JSON string
    json_str = json.dumps(data_dict, indent=4)
    # Print the JSON string
    return json_str