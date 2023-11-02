import csv
import json
import os
import pandas as pd

def file_upload(file, conference_id):
    app_folder = 'app'

    # Define the path to the vector_db folder within the app folder
    files_folder = os.path.join(app_folder, 'files')

    # Check if the vector_db folder exists, and create it if it doesn't
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)
    
    # Check if the uploaded file is a CSV file
    if file.filename.endswith(".csv"):
        # Generate a unique file path within the upload folder
        file_path = os.path.join(files_folder, 'sessions'+conference_id+'.csv')

        # Save the uploaded CSV file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())            
        
        # createVectorDb(conference_id)
        
        return {"original_filename": file.filename}
    
    elif file.filename.endswith(".json"): # Check if the uploaded file is a JSON file
        file_path = os.path.join(files_folder, 'sessions'+conference_id+'.json')
        
        # Save the uploaded JSON file to disk
        with open(file_path, "wb") as f:
            f.write(file.file.read())
            
        # Load the JSON file into memory
        with open(file_path, "r") as f:
            data = json.load(f)
            
        csv_file_path = os.path.join(files_folder, 'sessions'+conference_id+'.csv')
        
        # write the json data to a csv file
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')
            
            # write the header (filed names) to the csv file
            header = data[0].keys()
            csv_writer.writerow(header)
            
            # write the values to the csv file
            for row in data:
                csv_writer.writerow(row.values())
                
        # createVectorDb(conference_id)
            
        return {"original_filename": file.filename}
    
    elif file.filename.endswith(".xlsx"):
        # Handle Excel files
        file_path = os.path.join(files_folder, 'sessions'+conference_id+'.xlsx')
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        
        # Read the Excel file into a DataFrame using pandas
        try:
            df = pd.read_excel(file_path)
            
            # Convert the DataFrame to CSV format
            csv_file_path = os.path.join(files_folder, 'sessions'+conference_id+'.csv')
            df.to_csv(csv_file_path, index=False, sep=';', encoding='utf-8')
            
            # createVectorDb(conference_id)

            return {"original_filename": file.filename}
        except Exception as e:
            return {"error": "Failed to process the Excel file: " + str(e)}

    else:
        return {"error": "Only CSV, JSON and Excel files are allowed."}