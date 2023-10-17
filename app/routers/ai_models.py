from fastapi import APIRouter, UploadFile
from pathlib import Path
from ..data_ingestion import createVectorDb
from ..data_query import query_document
import os
import logging
import csv
import json

router = APIRouter()

@router.post("/query_document")
async def query_document_endpoint(question: str):
    answer = query_document(question)
    return {"answer": answer}

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile):
    
    app_folder = 'app'

    # Define the path to the vector_db folder within the app folder
    files_folder = os.path.join(app_folder, 'files')

    # Check if the vector_db folder exists, and create it if it doesn't
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)
    
    # Check if the uploaded file is a CSV file
    if file.filename.endswith(".csv"):
        # Generate a unique file path within the upload folder
        file_path = os.path.join(files_folder, 'sessions.csv')

        logging.info("Uploading file to %s" % file_path)
        
        # Save the uploaded CSV file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())            
        
        logging.info("Creating vector database")

        createVectorDb()
        
        logging.info("Vector database created")
        return {"filename": file.filename}
    
    elif file.filename.endswith(".json"): # Check if the uploaded file is a JSON file
        file_path = os.path.join(files_folder, 'sessions.json')
        
        # Save the uploaded JSON file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())
            
        # Load the JSON file into memory
        with open(file_path, "r") as f:
            data = json.load(f)
            
        csv_file_path = os.path.join(files_folder, 'sessions.csv')
        
        # write the json data to a csv file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')
            
            # write the header (filed names) to the csv file
            header = data[0].keys()
            csv_writer.writerow(header)
            
            # write the values to the csv file
            for row in data:
                csv_writer.writerow(row.values())
                
        createVectorDb()
            
        return {"filename": file.filename}
    else:
        return {"error": "Only CSV an JSON files are allowed."}