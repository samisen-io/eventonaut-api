FROM python:3.10-slim

WORKDIR /app 

 
COPY . .

# Update and install libgl
RUN apt-get clean
RUN apt-get update  
RUN apt-get install -y libgl1-mesa-glx
# RUN apt-get install -y libgl1-mesa-glx
#  COPY ./requirements.txt /app/requirements.txt
 RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
#  RUN apt-get install -y libgl1-mesa-glx 
#  RUN apt-get install -y libglib2.0-0

 CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
