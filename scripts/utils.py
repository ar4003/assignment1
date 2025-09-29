import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import colorlog
import time

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup colored logging with file and console output"""
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('ai_automation')
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_filename = f'logs/automation_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def save_data_to_csv(data: List[Dict], filename: str, directory: str = 'data') -> str:
    """Save data to CSV file"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    return filepath

def load_data_from_csv(filename: str, directory: str = 'data') -> List[Dict]:
    """Load data from CSV file"""
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath, encoding='utf-8')
    df = df.fillna('')  # Replace NaN with empty strings
    
    return df.to_dict('records')

def save_json(data: Any, filename: str, directory: str = 'output') -> str:
    """Save data to JSON file"""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath

def load_json(filename: str, directory: str = 'output') -> Any:
    """Load data from JSON file"""
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text or pd.isna(text):
        return ""
    
    text = str(text)
    text = ' '.join(text.split())
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    return text.strip()

def get_current_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def add_delay(delay_type: str = 'default'):
    """Add delay to avoid rate limiting"""
    delays = {
        'openai': 1,
        'google_trends': 2,
        'google_sheets': 0.5,
        'default': 1
    }
    
    time.sleep(delays.get(delay_type, 1))

def create_sample_data() -> List[Dict]:
    """Create sample data for testing"""
    return [
        {
            'keyword': 'ssc cgl admit card 2024',
            'interest_score': 85,
            'category': 'Admit Card',
            'status': 'Pending',
            'approval': 'Pending',
            'ai_confidence': 'High',
            'ai_reasoning': 'Contains admit card related terms',
            'web_search_summary': 'SSC CGL admit card trending',
            'related_queries': 'ssc.nic.in, admit card download',
            'top_regions': 'Delhi, Maharashtra, UP',
            'date_extracted': get_current_timestamp(),
            'categorized_at': get_current_timestamp(),
            'instagram_link': '',
            'blog_link': '',
            'youtube_reel_link': '',
            'youtube_thumbnail_link': '',
            'published_timestamp': ''
        },
        {
            'keyword': 'neet result 2024',
            'interest_score': 92,
            'category': 'Result',
            'status': 'Run GPT',  # This one approved for content generation
            'approval': 'Approved',
            'ai_confidence': 'High',
            'ai_reasoning': 'Clear result announcement pattern',
            'web_search_summary': 'NEET UG result declared with merit list',
            'related_queries': 'nta.ac.in, neet scorecard, merit list',
            'top_regions': 'Tamil Nadu, Karnataka, AP',
            'date_extracted': get_current_timestamp(),
            'categorized_at': get_current_timestamp(),
            'instagram_link': '',
            'blog_link': '',
            'youtube_reel_link': '',
            'youtube_thumbnail_link': '',
            'published_timestamp': ''
        }
    ]
