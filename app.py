import os
import json
from flask import Flask, send_file, request
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1bcWaXcgxzNeh-D1OrmRkX7v5dssiHspWwZYwtbIeF24'  # Replace with your Google Sheet ID
RANGE_NAME = 'Sheet1!A:L'  # Adjust the range as per your sheet structure

def get_google_sheets_service():
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json is None:
        raise ValueError("No Google credentials found in environment variables")
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

@app.route('/')
def home():
    return send_file("spy.gif", mimetype="image/gif")

@app.route('/image/<recipient_email>')
def spy_pixel(recipient_email):
    filename = "pixel.png"
    user_agent = request.headers.get('User-Agent')
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    get_ip = request.remote_addr

    data = '{"country_code":"Not found","country_name":"Not found","city":"Not found","postal":"Not found","latitude":"Not found","longitude":"Not found","IPv4":"IP Not found","state":"Not found"}'

    log_entry = [recipient_email, timestamp, user_agent, get_ip, data]

    try:
        service = get_google_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                       range=RANGE_NAME,
                                       valueInputOption='RAW',
                                       insertDataOption='INSERT_ROWS',
                                       body={'values': [log_entry]}).execute()
        logging.info(f"Successfully wrote to Google Sheets: {result}")
    except Exception as e:
        logging.error(f"Error writing to Google Sheets: {e}")
        return "Internal Server Error", 500

    return send_file(filename, mimetype="image/png")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
