import os
import io
import mimetypes
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# ---- Configuration ----
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/photoslibrary.appendonly"
]
FOLDER_ID = '12-_gisU2aV1-LOd0nu6_y5NmkHD-JCUr'  # Replace this
LOCAL_FOLDER = '/tmp/sharex_photos'

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_console()  # for headless
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_drive_service(creds):
    return build('drive', 'v3', credentials=creds)

def get_photos_upload_url(image_path, creds):
    upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-File-Name': os.path.basename(image_path),
        'X-Goog-Upload-Protocol': 'raw'
    }
    with open(image_path, 'rb') as img:
        response = requests.post(upload_url, headers=headers, data=img)
    return response.text

def create_photo(creds, upload_token):
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-type': 'application/json'
    }
    json_data = {
        "newMediaItems": [{
            "simpleMediaItem": {"uploadToken": upload_token}
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

    os.makedirs(LOCAL_FOLDER, exist_ok=True)

    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        spaces='drive',
        fields="files(id, name, mimeType)"
    ).execute()
    files = results.get('files', [])

    for file in files:
        file_id = file['id']
        filename = file['name']
        local_path = os.path.join(LOCAL_FOLDER, filename)

        # Download from Drive
        request = drive_service.files().get_media(fileId=file_id)
        with open(local_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        # Upload to Google Photos
        upload_token = get_photos_upload_url(local_path, creds)
        if create_photo(creds, upload_token):
            print(f"Uploaded: {filename}")
            drive_service.files().delete(fileId=file_id).execute()
            os.remove(local_path)
        else:
            print(f"Failed to upload: {filename}")

if __name__ == "__main__":
    process_photos()