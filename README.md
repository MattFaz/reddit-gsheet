# Reddit to Google Sheets

This script fetches your saved and upvoted Reddit posts and adds them to a Google Sheet.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up Google Cloud Project and enable Google Sheets API
   - Create a project at [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Sheets API
   - Create a service account:
     - Go to "Credentials" and click "Create Credentials" > "Service Account"
     - Fill in the service account details and click "Create"
     - Grant the service account the "Editor" role for Google Sheets
     - Create a key for the service account (JSON format)
     - Download the JSON key file and rename it to `credentials.json` in this directory
   - Share your Google Sheet with the service account email address (found in the credentials.json as "client_email")

4. Configure your environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env`:
     - Set `SPREADSHEET_ID` to your Google Sheet ID (found in the URL)
     - Set `SHEET_NAME` if you want to use a different sheet name (default is "RedditLinks")
     - Set `SERVICE_ACCOUNT_FILE` path if you're using a different filename (default is "credentials.json")
     - Update the Reddit feed URLs if needed

## Usage

Run the script manually:
```
python main.py
```

### Setting up scheduled runs

#### On Linux/Mac (using cron):
Add a cron job to run hourly:
```
0 * * * * cd /path/to/reddit-gsheet && /path/to/python main.py >> /path/to/log.txt 2>&1
```

#### On Windows (using Task Scheduler):
Create a batch file `run_script.bat`:
```
@echo off
cd /path/to/reddit-gsheet
python main.py
```
Then set up a scheduled task to run this batch file hourly.

## Notes

- The script stores links in your Google Sheet with date, title, URL, and whether it was saved or upvoted
- Posts are sorted by date (oldest first) before being added to the sheet
- It checks for duplicates to avoid adding the same link twice
- A User-Agent header is included in the Reddit API requests to follow best practices
- The authentication uses a service account, which is ideal for automated scripts
- Configuration is stored in the `.env` file for easy updates 