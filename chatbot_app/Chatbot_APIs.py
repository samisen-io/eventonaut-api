import os
import shutil
from fastapi import FastAPI, File, UploadFile,Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from chatbot_app.Chatbot_Data_Ingestion import createVectorDb
from chatbot_app.Chatbot_Data_Retrival import query_document
from pathlib import Path

app = FastAPI()
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/query_document")
async def query_document_endpoint(question: str):
    answer = query_document(question)
    return {"answer": answer}

upload_folder = "chatbot_app/files"
Path(upload_folder).mkdir(parents=True, exist_ok=True)

@app.post("/upload_csv_file/")
async def upload_csv_file(file: UploadFile):
    # Check if the uploaded file is a CSV file
    if file.filename.endswith(".csv"):
        # Generate a unique file path within the upload folder
        file_path = os.path.join(upload_folder, file.filename)
        
        # Save the uploaded CSV file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        createVectorDb()
        
        return {"filename": file.filename}
    else:
        return {"error": "Only CSV files are allowed."}
    