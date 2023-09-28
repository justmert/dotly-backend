# Dotly Backend
---

### Overview
This is the backend of the Dotly project. It is written in Python and uses FastAPI framework. It uses Firebase for authentication and database. It uses Subscan API for Polkadot/Kusama blockchain data.

If you want to **run the backend locally**, you need to create a Firebase project and a Subscan API key. You can find the instructions below.

### Setup
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