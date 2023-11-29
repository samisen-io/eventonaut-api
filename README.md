# Conference Assistant API

This API is developed to work with Conference Assistant app and Conference Buddy app and provides all the back-end functionality and AI features for those apps

## Setup

1. Install Python 3.10 or higher([3.10.7](https://www.python.org/downloads/release/python-3107/) is recommended). You can download it from [here](https://www.python.org/downloads/)
2. Install PostgreSQL. You can download it from [here](https://www.postgresql.org/download/)
3. Clone this repository
>Note: Steps 4 to 6 are **optional** but recommended. Jump to step 7 to continue
4. After installing Python, Install virtualenv using
 ```
 pip install virtualenv
 ```
5. The following command will create a python virtualenv in which ever directory you are in with the name _myenv_
```
python -m venv myenv
```
6. Now to activate the virtualenv using the following commad in the same directory that it was installed in
```
myenv\Scripts\activate
```
>Note: use the following commad to deactivate the virtualenv
```
deactivate
```
7. Install the required Python packages using
```
pip install -r requirements.txt
```

## Configuration

1. Create a _.env_ file in the root directory of the project
2. Add the following environment variables to the _.env_ file and fill in all the appropriate values

```
OPENAI_API_KEY= #Add Open AI key here
SECRET_KEY = #Add a Secret key for creating access token here
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL_ADDRESS = postgresql://username:password@localhost:5432/database_name #Replace username, password and database_name with your actual PostgreSQL username, password and database name for your application

EMAIL_ADDRESS = #Add an email you want to send you mails from
EMAIL_PASSWORD = #Add you email password
OTP_EXPIRE = 300

REFRESH_TOKEN_SECRET_KEY = #Add a Secret key for creating refresh token here
REFRESH_TOKEN_EXPIRE_MINUTES = 90
```
Replace the appropriate values with the actual values

## Build & Run

1. Run the following command to start the application
```
uvicorn app.main:app --reload
```
The application will be available at http://localhost:8000
