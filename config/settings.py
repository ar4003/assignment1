import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APIPIPE_API_KEY = os.getenv('APIPIPE_API_KEY')
    APIPIPE_API_BASE_URL = "https://aipipe.org/openrouter/v1/chat/completions"

    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'config/google_credentials.json')
    GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'AI Social Media Automation')
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    JOB_KEYWORDS = [
        'admit card 2025', 'hall ticket download', 'ssc admit card', 'bank po admit card', 'upsc admit card',
        'railway admit card', 'police admit card', 'teacher admit card', 'clerk admit card', 'result 2025',
        'merit list', 'cut off marks', 'ssc result', 'bank po result', 'upsc result', 'neet result', 'jee result',
        'railway result', 'police result', 'teacher result', 'job notification 2025', 'recruitment notification',
        'government job', 'sarkari job', 'bank recruitment', 'railway job', 'ssc notification', 'upsc vacancy',
        'police recruitment', 'teacher recruitment', 'clerk job', 'government vacancy', 'apply online'
    ]

    STATUS_PENDING = 'Pending'
    STATUS_RUN_GPT = 'Run GPT'
    STATUS_POST_LIVE = 'Post Live'
    STATUS_PUBLISHED = 'Published'

    CATEGORY_ADMIT_CARD = 'Admit Card'
    CATEGORY_RESULT = 'Result'
    CATEGORY_JOB_NOTIFICATION = 'Job Notification'
    CATEGORY_NOT_RELEVANT = 'Not Relevant'
    VALID_CATEGORIES = [
        CATEGORY_ADMIT_CARD, CATEGORY_RESULT, CATEGORY_JOB_NOTIFICATION, CATEGORY_NOT_RELEVANT
    ]

    SHEET_HEADERS = [
        'Keyword', 'Interest Score', 'Category', 'Status', 'Approval',
        'AI Confidence', 'AI Reasoning', 'Web Search Summary',
        'Instagram Link', 'Blog Link', 'YouTube Reel Link', 'YouTube Thumbnail Link',
        'Published Timestamp', 'Date Extracted', 'Categorized At', 'Related Queries', 'Top Regions'
    ]

    @classmethod
    def validate_config(cls):
        errors = []
        if not cls.APIPIPE_API_KEY:
            errors.append("APIPIPE_API_KEY is required")
        if cls.GOOGLE_SHEET_ID and not os.path.exists(cls.GOOGLE_APPLICATION_CREDENTIALS):
            errors.append(f"Google credentials not found: {cls.GOOGLE_APPLICATION_CREDENTIALS}")
        for directory in ['data', 'output', 'logs', 'config']:
            os.makedirs(directory, exist_ok=True)
        return errors

settings = Settings()
