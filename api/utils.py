from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv


load_dotenv()
def authenticate_drive():
#   To publish the code to github, the json file path must be called
# through the environment, or else the commit will be blocked or the key will be disabled.
  credentials = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON_FILE_PATH")
   )
  drive_service = build('drive', 'v3', credentials=credentials)
  
  return drive_service

service = authenticate_drive()

def get_folder_id(folder_name):
  drive_service = authenticate_drive()
  query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
  results = drive_service.files().list(q=query, fields="files(id, name)").execute()
  files = results.get('files', [])
  if files:
      return files[0]['id']
  return None

def upload_file(file_path, file_name, mimetype="video/mp4"):
    service = authenticate_drive()
    file_metadata = {
        'name': file_name,
        'mimeType': mimetype,
    }
    media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()
    read_permissions = {
       "type": "anyone",
       "role": "reader"
    }
    write_permissions = {
       "type": "user",
       "role": "writer",
       "emailAddress": "giahuy2003.peterpackerson@gmail.com"
    }
    service.permissions().create(
       fileId=file.get('id'),
       body=read_permissions
    ).execute()
    service.permissions().create(
       fileId=file.get("id"),
       body=write_permissions
    ).execute()
    return file.get('id')

def list_all_files():
   response = service.files().list(
      spaces="drive",
      fields="files(id, name, mimeType, size, createdTime)"
   ).execute()
   return response.get("files", [])

def get_specific_file(id):
   try:
      response = service.files().get(
         fileId=id,
         fields="id, name, mimeType, size, createdTime"
      ).execute()
      return response
   except HttpError as e:
      return
   
def delete_specific_file(id):
   try:
      response = service.files().delete(fileId=id).execute()
      return response
   except Exception as e:
      raise HttpError(e)
      

   # if not files:
   #    print(f"No files found.")
   # else:
   #    for file in files:
   #       print(f"File ID: {file.get('id')}, 
   #             Name: {file.get('name')}, 
   #             Type: {file.get('mimeType')},
   #             Size: {file.get('size')}, 
   #             Time: {file.get('createdTime')}")

# file_path = "Videos/videotest2.mp4"
# file_name = "my_video_2.mp4"
# upload_video_file(authenticate_drive(), file_path, file_name)