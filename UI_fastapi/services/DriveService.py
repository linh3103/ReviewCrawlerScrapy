import requests
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..app.config import settings

def get_files():
    creds, _ = google.auth.load_credentials_from_file(
        settings.GOOGLE_SERVICES_CREDENTIALS
    )

    try:
        service = build("drive", "v3", credentials=creds)
        files = []
        page_token = None

        while True:
            response = ( service.files().list(
                    q='mimeType="application/vnd.google-apps.spreadsheet" and trashed=false',
                    spaces='drive',
                    fields='nextPageToken, files(id, name, webViewLink)',
                    pageToken=page_token
                ).execute()
            )

            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

    return files
