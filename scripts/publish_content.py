import sys
import os
import gspread
from google.oauth2.service_account import Credentials
from config.settings import settings
from scripts.utils import setup_logging

def mock_publish_instagram(caption, hashtags, doc_link):
    print(f"[Mock Instagram] Caption preview: {caption[:30]}... Link: {doc_link}")

def mock_publish_blog(title, content, links):
    print(f"[Mock Blog] Title: {title} Links: {', '.join(links)}")

def mock_publish_youtube(script, thumbnail):
    print(f"[Mock YouTube] Script preview: {script[:30]}... Thumbnail: {thumbnail}")

class Publisher:
    def __init__(self):
        self.logger = setup_logging(settings.LOG_LEVEL)
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        self.credentials = Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes)
        self.client = gspread.authorize(self.credentials)

    def open_sheet(self):
        try:
            if settings.GOOGLE_SHEET_ID:
                sheet = self.client.open_by_key(settings.GOOGLE_SHEET_ID)
            else:
                sheet = self.client.open(settings.GOOGLE_SHEET_NAME)
            return sheet.worksheet('AI Automation Data')
        except Exception as e:
            self.logger.error(f"Error opening Google Sheet: {e}")
            return None

    def get_rows(self, worksheet):
        return worksheet.get_all_records()

    def update_status(self, worksheet, row_num, status):
        worksheet.update(f'D{row_num}', status)  # Assuming Status in D column

    def run(self):
        worksheet = self.open_sheet()
        if not worksheet:
            self.logger.error("Could not access worksheet.")
            return False
        
        rows = self.get_rows(worksheet)
        for idx, row in enumerate(rows, start=2):  # Data starts after header row 1
            status = row.get('Status')
            approval = row.get('Approval')
            keyword = row.get('Keyword')
            if approval != 'Approved' or status == 'Not Relevant':
                self.logger.info(f"Skipping '{keyword}' due to status or approval.")
                continue
            if status == 'Published':
                self.logger.info(f"Already published '{keyword}'. Skipping.")
                continue

            # Mock publish calls
            mock_publish_instagram("Sample caption with #hashtag", "#hashtag", row.get('Instagram Link'))
            mock_publish_blog(keyword, "Sample content with links", [row.get('Blog Link')])
            mock_publish_youtube("Sample reel script", row.get('Youtube Thumbnail Link'))

            # Update status in sheet after 'publishing'
            self.update_status(worksheet, idx, "Published")
            self.logger.info(f"Published content for '{keyword}'.")

        self.logger.info("Publishing run complete.")
        return True

def main():
    errors = settings.validate_config()
    if errors:
        print("Config errors:")
        for e in errors:
            print(f"  {e}")
        return
    publisher = Publisher()
    publisher.run()

if __name__ == "__main__":
    main()

"""

# Disclaimer:                                      
# This script is a mock publishing demo.           
# Actual Instagram, Blog, YouTube API integration 
# should replace the mock_publish_* functions.     
#                                                   
# How to run:                                       
# 1. Place this file as scripts/publish_content.py 
# 2. Run with: python -m scripts.publish_content    
# 3. Check updates in Google Sheet status column   

"""
