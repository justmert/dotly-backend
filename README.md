# Dotly Backend

### Overview
This is the backend of the Dotly project. It is written in Python and uses FastAPI framework. It uses Firebase for authentication and database. It uses Subscan API for Polkadot/Kusama blockchain data.

If you want to **run the backend locally with docker**, you need to create a Firebase project and a Subscan API key. You can find the instructions below.

### Setup with Docker
- **Clone this repository**
- **Create Firebase Admin SDK file and put it on root folder**
  - Go to https://console.firebase.google.com/
  - Create a project (name: dotly-demo)
  - Open Cloud Firestore and click create database 
  - Select "Production Mode" and click "Enable", select a location and click "Enable"
  - After database created, click "Start Collection" button
  - Create a collection and fill like above, then save
    - Collection ID: users
    - Document ID: admin
    - Field: username, Type: String, Value: admin
    - Field: password, Type: String, Value: dotly123
  - Go to project settings (on left sidebar (Project Overview), click gear icon)
  - Note your project id, we will use it at next step as {YOUR_FIREBASE_PROJECT_ID}
  - Go to service accounts tab
  - Select **Python** and click "Generate new private key" button
  - Rename the downloaded file to **dotly-admin-sdk.json** and put it on root folder
- **Create Subscan API Key**
  - https://pro.subscan.io/ - Create an account here
  - Login and get your free api key from https://pro.subscan.io/api_service (there is an arrow in my services container end of the row, click that and click the "add" button, you can name it whatever you want)
  - Note that API key, we will use at next step as {YOUR_SUBSCAN_API_KEY}
- **Generate a docker build**
    ```
    docker build -t dotly-backend .
    ```
- **Run the server with environment variables**
    ```
    docker run -p 8000:8000 -e SUBSCAN_API_KEY={YOUR_SUBSCAN_API_KEY} -e FIREBASE_PROJECT_ID={YOUR_FIREBASE_PROJECT_ID} -e FIREBASE_ADMIN_SDK_NAME="dotly-admin-sdk.json" -e API_SECRET_KEY="6807b50c66fe2ffa7c68af240587fe44a35bf505f564e7d2344739ecca514723" -e ADMIN_PASSWORD="dotly123" -e ADMIN_USERNAME="admin" dotly-backend
    ```

Your app will be running on http://localhost:8000 and you can see the docs on http://localhost:8000/docs

### Setup without Docker
- **Clone this repository**
- **Open repo directory in terminal and create a python environment**
  - ```$ python3 -m venv myenv```
  - ```$ source myenv/bin/activate```
- **Create Firebase Admin SDK file and put it on root folder**
  - Go to https://console.firebase.google.com/
  - Create a project (name: dotly-demo)
  - Open Cloud Firestore and click create database 
  - Select "Production Mode" and click "Enable", select a location and click "Enable"
  - After database created, click "Start Collection" button
  - Create a collection and fill like above, then save
    - Collection ID: users
    - Document ID: admin
    - Field: username, Type: String, Value: admin
    - Field: password, Type: String, Value: dotly123
  - Go to project settings (on left sidebar (Project Overview), click gear icon)
  - Note your project id, we will use it at next step as {YOUR_FIREBASE_PROJECT_ID}
  - Go to service accounts tab
  - Select **Python** and click "Generate new private key" button
  - Rename the downloaded file to **dotly-admin-sdk.json** and put it on root folder
- **Create Subscan API Key**
  - https://pro.subscan.io/ - Create an account here
  - Login and get your free api key from https://pro.subscan.io/api_service (there is an arrow in my services container end of the row, click that and click the "add" button, you can name it whatever you want)
  - Note that API key, we will use at next step as {YOUR_SUBSCAN_API_KEY}
- **Create **.env** file with the following content on root folder**
  ```
  SUBSCAN_API_KEY={YOUR_SUBSCAN_API_KEY}
  FIREBASE_PROJECT_ID={YOUR_FIREBASE_PROJECT_ID}
  FIREBASE_ADMIN_SDK_NAME="dotly-admin-sdk.json"
  API_SECRET_KEY="6807b50c66fe2ffa7c68af240587fe44a35bf505f564e7d2344739ecca514723"
  ADMIN_PASSWORD="dotly123"
  ADMIN_USERNAME="admin"
  ```
- **Install dependencies**
    ```$ pip3 install -r requirements.txt```
- **Run the server**
    ```$ python3 -m uvicorn api.api:app --host 0.0.0.0 --port 8000```

Your app will be running on http://localhost:8000 and you can see the docs on http://localhost:8000/docs

### How to Run Tests
Run this command from root, this will run all tests in tests folder
```pytest tests/*```

### Get Bearer Token
- Visit ```http://localhost:8000/docs```after you run server.
- Create user to get token
![Screenshot 2023-09-28 at 17 38 47](https://github.com/justmert/dotly-backend/assets/37740842/413e6652-c33a-4367-bc4d-0294f45865e0)
- Use created user to get bearer token
![Screenshot 2023-09-28 at 17 40 04](https://github.com/justmert/dotly-backend/assets/37740842/89227890-8e3a-4a29-9dcc-fc90fc8fc026)
- Save this bearer token, we will use at frontend (If you want to use backend on http://localhost:8000/docs use this bearer token as authorization, click authorize button right top of the page and paste this bearer token, by this way you will be authenticated=

### How to Run Tests
Run this command from **dotly-backend docker terminal**, this will run all tests in tests folder
```pytest tests/*```
