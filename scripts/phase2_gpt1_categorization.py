import sys
import os
import json
import time
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from scripts.utils import (
    setup_logging, load_data_from_csv, save_data_to_csv,
    get_current_timestamp, clean_text, add_delay
)

class ApiPipeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = settings.APIPIPE_API_BASE_URL

    def generate_text(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-4.1-nano",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

class GPT1CategorizationAgent:
    def __init__(self):
        self.logger = setup_logging(settings.LOG_LEVEL)
        self.client = ApiPipeClient(settings.APIPIPE_API_KEY)
        self.logger.info("✅ ApiPipe client initialized successfully")

    def perform_web_search(self, keyword):
        keyword_lower = keyword.lower()
        search_context = []
        admit_indicators = ['admit card', 'hall ticket', 'call letter', 'download']
        if any(indicator in keyword_lower for indicator in admit_indicators):
            search_context.append("Found admit card indicator in keyword")
        result_indicators = ['result', 'merit list', 'cut off', 'declared', 'scorecard']
        if any(indicator in keyword_lower for indicator in result_indicators):
            search_context.append("Found result indicator in keyword")
        job_indicators = ['job', 'recruitment', 'notification', 'vacancy', 'hiring']
        if any(indicator in keyword_lower for indicator in job_indicators):
            search_context.append("Found job notification indicator in keyword")
        gov_indicators = ['ssc', 'upsc', 'bank', 'railway', 'neet', 'jee', 'government']
        if any(indicator in keyword_lower for indicator in gov_indicators):
            search_context.append("Found government/education context")
        web_context = "; ".join(search_context) if search_context else "No specific job-related context found"
        return web_context

    def get_categorization_prompt(self):
        return """You are an expert AI agent specialized in categorizing job-related trending topics for India.

TASK: Categorize the keyword into EXACTLY ONE of these 4 categories:

1. Admit Card - Exam admit cards, hall tickets, call letters
2. Result - Exam results, merit lists, cut-off marks
3. Job Notification - Job openings, recruitment announcements
4. Not Relevant - Topics not related to jobs/exams/education

ANALYSIS DATA:
Keyword: {keyword}
Interest Score: {interest_score}
Related Queries: {related_queries}
Web Search Context: {web_context}

INSTRUCTIONS:
- Be strict - if not clearly job/exam related, mark as "Not Relevant"
- Focus on Indian job market and government exams
- Use web search context for accurate categorization

RESPONSE FORMAT (JSON only):
{{
    "category": "Exact category name from the 4 options above",
    "confidence": "High/Medium/Low",
    "reasoning": "Brief explanation (2-3 sentences)"
}}"""

    def categorize_keyword(self, entry, retries=3, backoff=5):
        web_context = ""
        try:
            web_context = self.perform_web_search(entry['keyword'])
            prompt = self.get_categorization_prompt().format(
                keyword=entry['keyword'],
                interest_score=entry.get('interest_score', 0),
                related_queries=entry.get('related_queries', ''),
                web_context=web_context
            )
            for attempt in range(retries):
                try:
                    response = self.client.generate_text(prompt)
                    text_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if not text_response:
                        text_response = response.get("text") or response.get("message") or ""
                    result = json.loads(text_response)
                    break
                except Exception as e:
                    self.logger.warning(
                        f"ApiPipe error or quota limit, retrying in {backoff}s (attempt {attempt + 1}/{retries}): {str(e)}"
                    )
                    time.sleep(backoff)
                    backoff *= 2
            else:
                self.logger.error("Max retries reached for ApiPipe. Marking as Not Relevant")
                return {
                    'category': settings.CATEGORY_NOT_RELEVANT,
                    'confidence': 'Low',
                    'reasoning': 'ApiPipe quota exceeded or errors',
                    'web_search_summary': web_context
                }
            category = result.get('category', settings.CATEGORY_NOT_RELEVANT)
            if category not in settings.VALID_CATEGORIES:
                category = settings.CATEGORY_NOT_RELEVANT
            return {
                'category': category,
                'confidence': result.get('confidence', 'Low'),
                'reasoning': result.get('reasoning', 'No reasoning provided'),
                'web_search_summary': web_context
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {
                'category': settings.CATEGORY_NOT_RELEVANT,
                'confidence': 'Low',
                'reasoning': f'JSON error: {e}',
                'web_search_summary': web_context
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {
                'category': settings.CATEGORY_NOT_RELEVANT,
                'confidence': 'Low',
                'reasoning': f'Error: {e}',
                'web_search_summary': web_context
            }

    def process_batch(self, data):
        self.logger.info("🤖 Starting GPT-1 Agent categorization with web search...")
        self.logger.info(f"📊 Processing {len(data)} entries")
        categorized_data = []
        for i, entry in enumerate(data, 1):
            self.logger.info(f"\n📝 Processing ({i}/{len(data)}): {entry['keyword']}")
            ai_result = self.categorize_keyword(entry)
            entry.update({
                'category': ai_result['category'],
                'ai_confidence': ai_result['confidence'],
                'ai_reasoning': ai_result['reasoning'],
                'web_search_summary': ai_result['web_search_summary'],
                'categorized_at': get_current_timestamp(),
                'status': settings.STATUS_PENDING
            })
            categorized_data.append(entry)
            self.logger.info(f"✅ Category: {ai_result['category']} (Confidence: {ai_result['confidence']})")
            add_delay('openai')
        return categorized_data

    def run(self):
        self.logger.info("🚀 Starting Phase 2: GPT-1 Agent Categorization")
        self.logger.info("=" * 60)
        try:
            self.logger.info(f"Current working directory: {os.getcwd()}")
            data_filename = 'phase1_trends_data.csv'
            data_path = os.path.join('data', data_filename)
            self.logger.info(f"Looking for data file at: {data_path}")
            self.logger.info(f"File exists: {os.path.exists(data_path)}")
            if not os.path.exists(data_path):
                self.logger.error(f"❌ File does not exist at {data_path}")
                self.logger.info("💡 Please run Phase 1 first: python main.py --phase 1")
                return False
            data = load_data_from_csv(data_filename)
            self.logger.info(f"📊 Loaded {len(data)} entries from Phase 1")
            if not data:
                self.logger.error("❌ No data to process")
                return False
            categorized_data = self.process_batch(data)
            if not categorized_data:
                self.logger.error("❌ No data categorized")
                return False
            output_filename = 'phase2_categorized_data.csv'
            filepath = save_data_to_csv(categorized_data, output_filename)
            self.logger.info("\n✅ Phase 2 Complete!")
            self.logger.info(f"🤖 Successfully categorized {len(categorized_data)} entries")
            self.logger.info(f"💾 Results saved to: {filepath}")
            self.logger.info("\n👉 Next: Review results and update status to 'Run GPT' for approved items")
            return True
        except Exception as e:
            self.logger.error(f"❌ Phase 2 failed: {e}")
            return False

def main():
    config_errors = settings.validate_config()
    if config_errors:
        print("❌ Configuration errors:")
        for error in config_errors:
            print(f"   {error}")
        return
    agent = GPT1CategorizationAgent()
    success = agent.run()
    if not success:
        exit(1)

if __name__ == "__main__":
    main()
