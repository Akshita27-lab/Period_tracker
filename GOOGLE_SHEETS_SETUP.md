# Google Sheets Integration Setup Guide

This guide will help you set up Google Sheets integration for logging user login data in your Period Tracker application.

## Prerequisites

- A Google account
- Basic knowledge of Google Sheets
- Python environment with the required packages installed

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Period Tracker")
5. Click "Create"

## Step 2: Enable Google Sheets API

1. In your Google Cloud project, go to the [APIs & Services > Library](https://console.cloud.google.com/apis/library)
2. Search for "Google Sheets API"
3. Click on "Google Sheets API"
4. Click "Enable"

## Step 3: Create Service Account Credentials

1. Go to [APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - **Name**: `period-tracker-sheets`
   - **Description**: `Service account for Period Tracker Google Sheets integration`
4. Click "Create and Continue"
5. For "Grant this service account access to project", select "Editor"
6. Click "Continue"
7. Click "Done"

## Step 4: Generate JSON Key File

1. In the Credentials page, find your service account and click on it
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Click "Create"
6. The JSON file will be downloaded automatically
7. **Important**: Keep this file secure and never commit it to version control

## Step 5: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Name it "Period Tracker User Logs" (or any name you prefer)
4. In the first row, add these headers:
   - A1: `Timestamp`
   - B1: `Action`
   - C1: `User_ID`
   - D1: `Email`
   - E1: `Name`
   - F1: `IP_Address`
5. Format the header row with bold text and background color
6. Copy the Sheet ID from the URL (it's the long string between `/d/` and `/edit`)

## Step 6: Share the Sheet with Service Account

1. In your Google Sheet, click "Share" (top right)
2. Add the service account email (found in your JSON file under `client_email`)
3. Give it "Editor" permissions
4. Click "Send" (you can uncheck "Notify people")

## Step 7: Configure the Application

1. Place your downloaded JSON file in your project directory
2. Update `google_sheets_config.py` with your actual values:

```python
# Your Google Sheets API credentials file path
CREDENTIALS_FILE = 'path/to/your/downloaded-credentials.json'

# Your Google Sheet ID (found in the URL)
SHEET_ID = 'your_actual_sheet_id_here'

# Sheet name where login data will be stored
LOGIN_SHEET_NAME = 'Sheet1'  # or whatever your sheet name is

# Column headers for the login data sheet
LOGIN_COLUMNS = ['Timestamp', 'Action', 'User_ID', 'Email', 'Name', 'IP_Address']
```

## Step 8: Test the Integration

1. Run your Flask application
2. Register a new user or log in with an existing user
3. Check your Google Sheet to see if the data is being logged

## Troubleshooting

### Common Issues:

1. **"File not found" error**
   - Make sure the path to your credentials file is correct
   - Use absolute paths if needed

2. **"Permission denied" error**
   - Ensure the service account email has Editor access to the sheet
   - Check that the sheet ID is correct

3. **"API not enabled" error**
   - Make sure Google Sheets API is enabled in your Google Cloud project

4. **"Invalid credentials" error**
   - Verify your JSON credentials file is valid and not corrupted
   - Check that the service account has the necessary permissions

### Security Best Practices:

1. **Never commit credentials to version control**
   - Add `*.json` to your `.gitignore` file
   - Use environment variables for sensitive data in production

2. **Limit permissions**
   - Only give the service account the minimum required permissions
   - Consider using a dedicated Google account for this integration

3. **Regular monitoring**
   - Check your Google Cloud Console for API usage
   - Monitor the sheet for any unusual activity

## Production Deployment

For production deployment, consider:

1. **Environment variables**: Store sensitive data in environment variables
2. **Credential rotation**: Regularly rotate your service account keys
3. **Monitoring**: Set up alerts for API usage and errors
4. **Backup**: Regularly backup your Google Sheet data

## Example Configuration for Production

```python
import os

CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'path/to/credentials.json')
SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', 'your_sheet_id')
LOGIN_SHEET_NAME = os.environ.get('GOOGLE_SHEET_NAME', 'Sheet1')
```

## Support

If you encounter issues:

1. Check the Google Cloud Console for error messages
2. Verify all configuration values are correct
3. Test with a simple Python script first
4. Check the Flask application logs for detailed error messages

## Data Privacy

Remember that this integration logs user login data to Google Sheets. Ensure you:

1. Inform users about data collection
2. Comply with relevant privacy laws (GDPR, CCPA, etc.)
3. Implement appropriate data retention policies
4. Provide users with options to delete their data if required 