# CMR2025 Downloader

A Python utility for automated download of the CMR2025 Challenge dataset from Google Drive.

## Features

- Authenticates with Google Drive API using OAuth2
- Lists and downloads all files from the CMR2025 dataset folder
- Tracks download progress with visual progress bars
- Verifies file integrity through size comparison
- Skips already downloaded files (resume capability)
- Detailed logging for monitoring and debugging

## Prerequisites

- Python 3.6+
- Google account with access to the CMR2025 dataset
- Google Cloud Platform project with Drive API enabled

## Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/cmr2025_downloader.git
   cd cmr2025_downloader
   ```

2. **Install required packages**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib tqdm
   ```

3. **Set up Google API credentials**
   - Visit the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select an existing one)
   - Enable the Google Drive API
   - Create OAuth credentials (Desktop application type)
   - Download the credentials as `credentials.json`
   - Place the downloaded file in the repository root directory

## Configuration

Create a `config` file in the repository root with the following content:

```json
{
    "google_drive_folder_id": "1VpycwaqJg50KBG2ED6hhJ0GnSCHU5ce-",
    "download_directory": "/path/to/your/download/location"
}
```

The configuration options are:
- `google_drive_folder_id`: The ID of the Google Drive folder containing CMR2025 dataset
- `download_directory`: Full path to the directory where files will be downloaded

## Usage

### Basic Usage
```bash
python download_drive.py
```

### Background Download (for long sessions)

To keep downloads running after disconnecting from the server:
```bash
nohup python download_drive.py > download.log 2>&1 &
```

To check download status:
```bash
tail -f download.log
```

## Authentication Process

When running the script for the first time:

1. A browser window will open requesting Google account login
2. You'll need to authorize the application to access Google Drive
3. If your app is unverified (normal for personal use), click "Advanced" and "Go to [Project] (unsafe)"
4. After successful authentication, a token will be saved locally for future use

**Important:** For unverified apps, add your email as a test user in the Google Cloud Console under "APIs & Services" > "OAuth consent screen" > "Test users".

## Troubleshooting

- **Token expired**: Delete the `token.json` file and run again
- **File not found**: Verify the folder ID in your config file
- **Permission denied**: Ensure your Google account has access to the CMR2025 dataset
- **Access denied**: Make sure your email is added as a test user in your Google Cloud project

## File Structure
```
cmr2025_downloader/
├── download_drive.py    # Main script file
├── config              # Configuration file
├── credentials.json    # Google API credentials (you must add this)
└── token.json         # Authentication token (auto-generated)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the CMR2025 Challenge organizers for making this dataset available
- Built using Google's official Python client libraries

## Disclaimer

This tool is provided as-is without warranty. Users are responsible for ensuring they have appropriate permissions to access and download the dataset. Usage of Google Drive API is subject to Google's terms of service.