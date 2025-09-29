"""
Phase 4: Google Sheets Integration
Integrate with Google Sheets for workflow management and content tracking
"""

import sys
import os
import gspread
from google.oauth2.service_account import Credentials

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings
from scripts.utils import setup_logging, load_data_from_csv

class GoogleSheetsIntegration:
    def __init__(self):
        self.logger = setup_logging(settings.LOG_LEVEL)
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        try:
            self.credentials = Credentials.from_service_account_file(
                settings.GOOGLE_APPLICATION_CREDENTIALS,
                scopes=self.scopes
            )
            self.client = gspread.authorize(self.credentials)
            self.logger.info("✅ Google Sheets authentication successful")
        except FileNotFoundError:
            self.logger.error(f"❌ Google credentials file not found: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
            self.client = None
        except Exception as e:
            self.logger.error(f"❌ Google Sheets authentication error: {str(e)}")
            self.client = None

    def open_spreadsheet(self):
        if not self.client:
            return None
        try:
            if settings.GOOGLE_SHEET_ID:
                spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
                self.logger.info(f"📊 Opened spreadsheet by ID: {settings.GOOGLE_SHEET_ID}")
            else:
                spreadsheet = self.client.open(settings.GOOGLE_SHEET_NAME)
                self.logger.info(f"📊 Opened spreadsheet by name: {settings.GOOGLE_SHEET_NAME}")
            return spreadsheet
        except gspread.SpreadsheetNotFound:
            self.logger.error(f"❌ Spreadsheet not found: {settings.GOOGLE_SHEET_ID or settings.GOOGLE_SHEET_NAME}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error opening spreadsheet: {str(e)}")
            return None

    def setup_worksheet(self, spreadsheet, worksheet_name='AI Automation Data'):
        try:
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                self.logger.info(f"  📋 Found existing worksheet: {worksheet_name}")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=len(settings.SHEET_HEADERS)
                )
                self.logger.info(f"  ➕ Created new worksheet: {worksheet_name}")
            worksheet.clear()
            worksheet.insert_row(settings.SHEET_HEADERS, 1)
            self.logger.info(f"  ✅ Updated headers for {worksheet_name}")
            return worksheet
        except Exception as e:
            self.logger.error(f"  ❌ Error setting up {worksheet_name}: {str(e)}")
            return None

    def upload_data_to_sheet(self, worksheet, data_file_name='updated_trends_data.csv'):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
        full_path = os.path.join(base_path, 'data', data_file_name)

        self.logger.info(f"Reading CSV file from: {full_path}")
        if not os.path.exists(full_path):
            self.logger.error(f"❌ Data file does not exist: {full_path}")
            return False
        try:
            data = load_data_from_csv(full_path)
            if not data:
                self.logger.warning("⚠️ No data to upload")
                return False
            upload_data = []
            for entry in data:
                row = []
                for header in settings.SHEET_HEADERS:
                    h = header.lower().replace(' ', '_')
                    row.append(str(entry.get(h, '')))
                upload_data.append(row)
            if upload_data:
                worksheet.batch_clear(["A2:Z1000"])
                worksheet.update(f"A2:Z{len(upload_data)+1}", upload_data)
                self.logger.info(f"  ✅ Uploaded {len(upload_data)} entries")
                return True
            return False
        except Exception as e:
            self.logger.error(f"  ❌ Error uploading data: {str(e)}")
            return False

    def run(self):
        self.logger.info("🚀 Starting Phase 4: Google Sheets Integration")
        self.logger.info("=" * 60)
        if not self.client:
            self.logger.error("❌ Cannot proceed without Google Sheets authentication")
            return False
        spreadsheet = self.open_spreadsheet()
        if not spreadsheet:
            self.logger.error("❌ Could not access spreadsheet")
            return False
        worksheet = self.setup_worksheet(spreadsheet, 'AI Automation Data')
        if not worksheet:
            self.logger.error("❌ Could not setup worksheet")
            return False
        if not self.upload_data_to_sheet(worksheet):
            self.logger.error("❌ Failed to upload data to Google Sheets")
            return False
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        self.logger.info("\n✅ Phase 4 Complete!")
        self.logger.info(f"🔗 Spreadsheet URL: {spreadsheet_url}")
        self.logger.info("💡 OPEN the spreadsheet URL to review and update statuses manually.")
        return True

def main():
    config_errors = settings.validate_config()
    if config_errors:
        print("❌ Configuration errors:")
        for err in config_errors:
            print(f"   {err}")
        return
    integration = GoogleSheetsIntegration()
    success = integration.run()
    if not success:
        exit(1)

if __name__ == "__main__":
    main()
