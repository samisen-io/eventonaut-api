import csv
import io
import json
from fastapi import HTTPException

import openpyxl

def find_delimiter(first_line):
    delimiters = [',', ';', '\t', '|']
    for delimiter in delimiters:
        if delimiter in first_line:
            return delimiter
    return ","  # Default to comma if no delimiter found

async def read_file_return_csv(contents, filename):
    if filename.endswith(".csv"):    
        try:
            contents_str = contents.decode("utf-8")
        except UnicodeDecodeError as e:
            raise HTTPException(status_code=400, detail="Unable to decode contents: " + str(e))
        first_line = contents_str.split('\n')[0]
        try:
            delimiter = find_delimiter(first_line)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Unable to find delimiter: " + str(e))
        try:
            reader  = csv.DictReader(io.StringIO(contents_str), delimiter=delimiter)
        except csv.Error as e:
            raise HTTPException(status_code=400, detail="Unable to read CSV: " + str(e))
        return reader
        
    elif filename.endswith(".json"):
        # Load the JSON file
        json_file = json.loads(contents)
        # Get the keys (column names) from the first dictionary in the list
        keys = json_file[0].keys()
        # Create a StringIO object to hold the CSV data
        output = io.StringIO()
        # Create a CSV writer object
        csv_file = csv.DictWriter(output, fieldnames=keys)
        # Write the header
        csv_file.writeheader()
        # Write the rows
        csv_file.writerows(json_file)
        # Get the CSV data as a string
        csv_data = output.getvalue()  
        csv_file = io.StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        return reader
    
    elif filename.endswith(".xlsx"):
        # Load the workbook
        wb = openpyxl.load_workbook(filename=io.BytesIO(contents))
        # Select the first sheet
        sheet = wb.active
        # Create a StringIO object to hold the CSV data
        output = io.StringIO()
        # Create a CSV writer object
        csv_file = csv.writer(output)
        # Write the rows
        for row in sheet.iter_rows(values_only=True):
            csv_file.writerow(row)
        # Get the CSV data as a string
        csv_data = output.getvalue()
        # Create a StringIO object from the CSV data
        csv_file = io.StringIO(csv_data)
        # Create a DictReader from the StringIO object
        reader = csv.DictReader(csv_file)
        return reader
    else:
        return {"error": "Only CSV, JSON and Excel files are allowed."}