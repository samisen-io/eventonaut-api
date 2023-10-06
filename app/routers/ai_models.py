from fastapi import APIRouter, UploadFile
from pathlib import Path
from ..data_ingestion import createVectorDb
from ..data_query import query_document
import os
import logging

router = APIRouter()

upload_folder = "../files"
Path(upload_folder).mkdir(parents=True, exist_ok=True)

@router.post("/query_document")
async def query_document_endpoint(question: str):
    answer = query_document(question)
    return {"answer": answer}

@router.post("/upload_csv_file/")
async def upload_csv_file(file: UploadFile):
    # Check if the uploaded file is a CSV file
    if file.filename.endswith(".csv"):
        # Generate a unique file path within the upload folder
        file_path = os.path.join(upload_folder, file.filename)

        logging.info("Uploading file to %s" % file_path)
        
        # Save the uploaded CSV file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        logging.info("Creating vector database")

        createVectorDb()
        
        logging.info("Vector database created")

        return {"filename": file.filename}
    else:
        return {"error": "Only CSV files are allowed."}