#class that provides methods to ingest data from a file



#function that takes filename and retrieves the fole to process it
def ingest_file(filename):
    #open file
    file = open(filename, "r")
    #read file
    file.read()
    validate_file(file)
    
    #close file
    file.close()
    #return file
    return file

#function to validate if file is csv or not
def validate_file(file):
    #check if file is csv
    if file.endswith(".csv"):
        #return true
        return True
    #else
    else:
        #return false
        return False