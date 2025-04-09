import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Google Sheets configuration
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "credentials.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "RedditLinks")

# Reddit feeds
SAVED_FEED = os.getenv("SAVED_FEED")
UPVOTED_FEED = os.getenv("UPVOTED_FEED")


def authenticate_google_sheets():
    """Authenticate with Google Sheets API using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=credentials)
        return service.spreadsheets()
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def get_latest_datetime(sheets):
    """Get the most recent date/time from Google Sheet to filter new entries."""
    try:
        result = (
            sheets.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A:D")
            .execute()
        )

        values = result.get("values", [])
        if not values:
            # Initialize with headers if sheet is empty
            sheets.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!A1:D1",
                valueInputOption="RAW",
                body={"values": [["Date", "Title", "Link", "Type"]]},
            ).execute()
            return None

        # Skip header row and find the most recent date/time
        # The sheet is sorted with oldest first, so the last row has the most recent date
        data_rows = values[1:]  # Skip header
        if not data_rows:
            return None

        # Get the last row's date/time (column A)
        latest_row = data_rows[-1]
        if len(latest_row) > 0:
            try:
                latest_datetime = latest_row[0]
                return latest_datetime
            except (IndexError, ValueError):
                return None

        return None
    except Exception as e:
        print(f"Error getting latest date/time: {e}")
        return None


def fetch_reddit_feed(feed_url, feed_type):
    """Fetch Reddit feed data."""
    headers = {"User-Agent": "python:reddit-feed-to-gsheet:v1.0 (by /u/M-fz)"}

    try:
        response = requests.get(feed_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            items = []

            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                items.append(
                    {
                        "date": datetime.fromtimestamp(
                            post_data.get("created_utc", 0)
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "title": post_data.get("title", "No Title"),
                        "link": f"https://www.reddit.com{post_data.get('permalink')}",
                        "type": feed_type,
                    }
                )

            return items
        else:
            print(f"Error fetching {feed_type} feed: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error processing {feed_type} feed: {e}")
        return []


def write_to_sheet(sheets, new_items):
    """Write new items to Google Sheet."""
    if not new_items:
        print("No new items to add.")
        return

    try:
        values = [
            [item["date"], item["title"], item["link"], item["type"]]
            for item in new_items
        ]

        # Append to the sheet
        sheets.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:D",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()

        print(f"Added {len(new_items)} new items to the sheet.")
    except Exception as e:
        print(f"Error writing to sheet: {e}")


def main():
    # Authenticate with Google Sheets
    sheets = authenticate_google_sheets()
    if not sheets:
        return

    # Get the latest date/time from the sheet
    latest_datetime = get_latest_datetime(sheets)

    # Fetch both feeds
    saved_items = fetch_reddit_feed(SAVED_FEED, "Saved")
    upvoted_items = fetch_reddit_feed(UPVOTED_FEED, "Upvoted")

    # Combine items
    all_items = saved_items + upvoted_items

    # Filter items newer than the latest date/time in the sheet
    if latest_datetime:
        new_items = [item for item in all_items if item["date"] > latest_datetime]
        print(f"Found {len(new_items)} items newer than {latest_datetime}")
    else:
        # If no existing entries, include all items
        new_items = all_items
        print(f"No existing entries found. Adding {len(new_items)} items.")

    # Sort items by date (oldest first)
    new_items.sort(key=lambda x: x["date"], reverse=False)

    # Write new items to the sheet
    write_to_sheet(sheets, new_items)


if __name__ == "__main__":
    main()
