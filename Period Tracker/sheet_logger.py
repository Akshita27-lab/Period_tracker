import gspread
from google.oauth2.service_account import Credentials
from google_sheets_config import CREDENTIALS_FILE, SHEET_ID, LOGIN_SHEET_NAME

def log_to_sheet(data):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet(LOGIN_SHEET_NAME)
    worksheet.append_row(data)
