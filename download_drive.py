import os
import json
import time
import logging
import requests
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm
import io

# Set up logging
output_dir = '/mnt/LiDXXLab_Files/ziyang/CMR2025'
os.makedirs(output_dir, exist_ok=True)
log_file = os.path.join(output_dir, f"gdrive_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def load_config():
    """Load configuration from config file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        raise

def authenticate():
    """Authenticate with Google Drive API."""
    creds = None
    # Token file stores the user's access and refresh tokens
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Check if token.json exists
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_info(json.loads(open(token_path).read()), SCOPES)
        except Exception as e:
            logging.warning(f"Error loading credentials: {e}")
    
    # If credentials don't exist or are invalid, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.warning(f"Failed to refresh credentials: {e}")
                creds = None
        
        # If still no valid credentials, authenticate with user
        if not creds:
            if not os.path.exists(credentials_path):
                logging.error("No credentials.json file found. Please download it from Google Cloud Console.")
                raise FileNotFoundError("credentials.json not found")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logging.error(f"Authentication failed: {e}")
                raise
    
    return creds

def list_files_in_folder(service, folder_id):
    """List all files in a Google Drive folder."""
    try:
        # List files in the folder
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name, size, md5Checksum)",
            pageSize=1000
        ).execute()
        items = results.get('files', [])
        
        if not items:
            logging.warning("No files found in the specified folder.")
            return []
            
        # Sort files by name
        items.sort(key=lambda x: x.get('name', ''))
        
        logging.info(f"Found {len(items)} files in the folder.")
        return items
    except Exception as e:
        logging.error(f"Error listing files in folder: {e}")
        raise

def download_file(service, file_id, file_name, download_path):
    """Download a file from Google Drive."""
    full_path = os.path.join(download_path, file_name)
    
    # Check if file already exists
    if os.path.exists(full_path):
        logging.info(f"File {file_name} already exists. Checking integrity...")
        
        # Could implement MD5 check here, but for simplicity, using file size
        try:
            file_metadata = service.files().get(fileId=file_id, fields="size").execute()
            remote_size = int(file_metadata.get('size', 0))
            local_size = os.path.getsize(full_path)
            
            if local_size == remote_size:
                logging.info(f"File {file_name} verified by size. Skipping download.")
                return True
            else:
                logging.warning(f"File {file_name} size mismatch. Re-downloading.")
        except Exception as e:
            logging.warning(f"Error checking file {file_name}: {e}. Will download again.")
    
    # Perform the download
    try:
        request = service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        
        # Create a downloader
        downloader = MediaIoBaseDownload(file_handle, request)
        
        done = False
        progress_bar = tqdm(total=100, desc=file_name)
        last_progress = 0
        
        while not done:
            status, done = downloader.next_chunk()
            if status:
                current_progress = int(status.progress() * 100)
                increment = current_progress - last_progress
                progress_bar.update(increment)
                last_progress = current_progress
        
        progress_bar.close()
        
        # Save the file
        file_handle.seek(0)
        with open(full_path, 'wb') as f:
            f.write(file_handle.read())
        
        logging.info(f"Successfully downloaded {file_name}")
        return True
    
    except Exception as e:
        logging.error(f"Error downloading {file_name}: {e}")
        return False
    
def main():
    """Main function to download files from Google Drive."""
    try:
        # Load configuration
        config = load_config()
        folder_id = config.get('google_drive_folder_id')
        download_dir = config.get('download_directory')
        
        if not folder_id or not download_dir:
            logging.error("Missing required configuration. Check config file.")
            return
        
        # Create download directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        # Authenticate
        logging.info("Authenticating with Google Drive...")
        creds = authenticate()
        
        # Create Drive API client
        service = build('drive', 'v3', credentials=creds)
        
        # List files in the folder
        logging.info(f"Listing files in folder {folder_id}...")
        files = list_files_in_folder(service, folder_id)
        
        # Download files
        successful = 0
        failed = 0
        skipped = 0
        
        for i, file in enumerate(files):
            file_id = file.get('id')
            file_name = file.get('name')
            
            logging.info(f"Processing file {i+1}/{len(files)}: {file_name}")
            
            try:
                result = download_file(service, file_id, file_name, download_dir)
                if result:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logging.error(f"Unexpected error with file {file_name}: {e}")
                failed += 1
        
        logging.info(f"Download summary: {successful} successful, {failed} failed, {skipped} skipped")
        
    except Exception as e:
        logging.error(f"Error in main process: {e}")

if __name__ == '__main__':
    main()