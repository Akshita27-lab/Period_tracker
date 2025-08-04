import gspread
from google.oauth2.service_account import Credentials

# Set up credentials and sheet info
CREDENTIALS_FILE = 'period-tracker-467708-e0f65cc96872.json'
SHEET_ID = '1IthWHfM13glPnffN3CN5xLvr2w4oefc07psMJfD8wks'
SHEET_NAME = 'Sheet1'

# Authenticate and open the sheet
scopes = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
gc = gspread.authorize(credentials)
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.worksheet(SHEET_NAME)

# Append a row (replace with your actual data)
worksheet.append_row(['2025-08-01 12:00', 'Login', 'user123', 'user@example.com', 'User Name', '127.0.0.1'])
print("Row added!")