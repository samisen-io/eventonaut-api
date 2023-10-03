from flask import Flask, request
import csv
import json
import random
import os

app = Flask(__name__) # Flask constructor

# A decorator used to tell the application
# which URL is associated function
@app.route('/')
def hello():
    return 'Hello World!!'

@app.route('/upload_csv', methods=['POST'])
def upload_csv_endpoint():
    # get the file from the request
    file = request.files['file']
    
    num = random.random()
    
    prediction_file_name = 'files/sessions.csv'
    file_path = os.path.join(os.path.dirname(__file__),prediction_file_name)
    
    # save the file to the server
    file.save(file_path)
    
    csvFilePath = file_path
    jsonFilePath = os.path.join(os.path.dirname(__file__),'json/sessions.json')
    
    csv_to_json(csvFilePath, jsonFilePath)
    
    return 'File uploaded successfully!!'

def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []
    
    # read csv file
    with open(csvFilePath, encoding='utf-8') as csvf:
        # load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf, delimiter=';')
    
        # convert each csv row into python dict
        for row in csvReader:
            jsonArray.append(row)
            
    # convert python jsonArray to JSON string and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)

if __name__=='__main__':
    app.run(debug=True)