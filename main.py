import os
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Configuration
scopes = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/photoslibrary.appendonly"
]
localFolder = '/tmp/sharex_photos'
folderID = 'folderID.txt'

def get_folder_id():
    if os.path.exists(folderID):
        with open(folderID, 'r') as f:
            return f.read().strip()
    idInput = input("Enter your Google Drive folder ID: ").strip()
    with open(folderID, 'w') as f:
        f.write(idInput)
    return idInput

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            authURL, _ = flow.authorization_url(prompt='consent')
            print(f"\nGo to this URL to authorize the app:\n{authURL}\n")
            code = input("Paste the authorization code here: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_drive_service(creds):
    return build('drive', 'v3', credentials=creds)

def get_photos_upload_url(imagePath, creds):
    uploadURL = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-File-Name': os.path.basename(imagePath),
        'X-Goog-Upload-Protocol': 'raw'
    }
    with open(imagePath, 'rb') as img:
        response = requests.post(uploadURL, headers=headers, data=img)
    return response.text

def create_photo(creds, uploadToken):
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-type': 'application/json'
    }
    json_data = {
        "newMediaItems": [{
            "simpleMediaItem": {"uploadToken": uploadToken}
        }]
    }
    response = requests.post(
        'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
        headers=headers,
        json=json_data
    )
    return response.status_code == 200

def process_photos():
    creds = authenticate()
    drive_service = get_drive_service(creds)
    idInput = get_folder_id()

    os.makedirs(localFolder, exist_ok=True)

    results = drive_service.files().list(
        q=f"'{idInput}' in parents and trashed = false",
        spaces='drive',
        fields="files(id, name, mimeType)"
    ).execute()
    files = results.get('files', [])

    for file in files:
        file_id = file['id']
        filename = file['name']
        localPath = os.path.join(localFolder, filename)

        # Download from Drive
        request = drive_service.files().get_media(fileId=file_id)
        with open(localPath, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        # Upload to Google Photos
        uploadToken = get_photos_upload_url(localPath, creds)
        if create_photo(creds, uploadToken):
            print(f"Uploaded: {filename}")
            drive_service.files().delete(fileId=file_id).execute()
            os.remove(localPath)
        else:
            print(f"Failed to upload: {filename}")

if __name__ == "__main__":
    process_photos()
