# Google Sheets Configuration
# You need to set up Google Sheets API and get these credentials

# Your Google Sheets API credentials file path
# Download from: https://console.cloud.google.com/apis/credentials

CREDENTIALS_FILE = 'period-tracker-467708-e0f65cc96872.json'
# Your Google Sheet ID (found in the URL of your sheet)
SHEET_ID = '1IthWHfM13glPnffN3CN5xLvr2w4oefc07psMJfD8wks'

# Sheet name where login data will be stored
LOGIN_SHEET_NAME = 'Sheet1'

# Column headers for the login data sheet
LOGIN_COLUMNS = ['Timestamp', 'Action', 'User_ID', 'Email', 'Name', 'IP_Address'] 