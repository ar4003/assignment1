import sys
import os
import json
import time
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from scripts.utils import setup_logging, load_data_from_csv, save_data_to_csv, save_json, get_current_timestamp, add_delay

class GPT2ContentGenerationAgent:
    """GPT-2 Agent for generating multi-platform content with ApiPipe"""

    def __init__(self):
        self.logger = setup_logging(settings.LOG_LEVEL)
        self.api_key = settings.APIPIPE_API_KEY
        self.base_url = settings.APIPIPE_API_BASE_URL
        if not self.api_key:
            raise ValueError("ApiPipe API key is not set")
        self.logger.info("✅ ApiPipe client initialized for content generation")

    def get_content_prompts(self):
        return {
            'instagram_post': """Create an engaging Instagram post for job seekers in India.

CONTENT DETAILS:
Category: {category}
Keyword: {keyword}
Context: {reasoning}

REQUIREMENTS:
- Create attractive, informative caption (150-200 words)
- Include relevant emojis naturally
- Add 15-20 targeted hashtags for Indian job market
- Make it engaging for students and job seekers
- Include clear call-to-action
- Use motivational and helpful tone

RESPONSE FORMAT (JSON):
{{
    "caption": "Instagram caption with emojis and engaging content",
    "hashtags": "#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5 #hashtag6 #hashtag7 #hashtag8 #hashtag9 #hashtag10 #hashtag11 #hashtag12 #hashtag13 #hashtag14 #hashtag15",
    "post_type": "Instagram Post"
}}""",

            'blog_article': """Create a comprehensive blog article for job seekers.

CONTENT DETAILS:
Category: {category}
Keyword: {keyword}
Context: {reasoning}

REQUIREMENTS:
- Write detailed article (400-500 words)
- SEO-optimized title with keyword
- Include relevant subheadings
- Add application process and important dates
- Include eligibility criteria if applicable
- Add disclaimer about checking official sources
- Include organization homepage link: https://jobyaari.com
- Make it informative and helpful

RESPONSE FORMAT (JSON):
{{
    "title": "SEO-optimized blog title with keyword",
    "content": "Full blog article with HTML subheadings <h2>, <h3> and proper formatting",
    "meta_description": "150-character SEO meta description",
    "homepage_link": "https://jobyaari.com"
}}""",

            'youtube_reel': """Create a YouTube Reel script for job-related content.

CONTENT DETAILS:
Category: {category}
Keyword: {keyword}
Context: {reasoning}

REQUIREMENTS:
- Create 30-60 second video script
- Write engaging description with keywords
- Include 10-15 relevant hashtags
- Add hook, main content, and strong CTA
- Make it informative yet concise
- Include visual cues for video creation

RESPONSE FORMAT (JSON):
{{
    "script": "Complete video script with timing cues [0-5s], [5-15s], etc.",
    "description": "YouTube description with keywords and engagement hooks",
    "hashtags": "#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5 #hashtag6 #hashtag7 #hashtag8 #hashtag9 #hashtag10",
    "duration": "30-60 seconds"
}}""",

            'youtube_thumbnail': """Create YouTube thumbnail design specifications.

CONTENT DETAILS:
Category: {category}
Keyword: {keyword}
Context: {reasoning}

REQUIREMENTS:
- Describe visual elements and layout
- Specify text overlay and fonts
- Include color scheme recommendations
- Make it click-worthy and professional
- Follow YouTube thumbnail best practices
- Ensure mobile readability

RESPONSE FORMAT (JSON):
{{
    "design_description": "Detailed visual description of thumbnail layout and elements",
    "text_overlay": "Main text to display on thumbnail",
    "color_scheme": "Primary and secondary colors with hex codes",
    "style": "Design style and mood (professional, modern, bold, etc.)"
}}"""
        }

    def generate_content_for_keyword(self, entry):
        status = entry.get('status')
        if status != settings.STATUS_RUN_GPT:
            self.logger.info(f"⏭️ Skipping {entry['keyword']} - status: {status}")
            return None
        if entry.get('category') == settings.CATEGORY_NOT_RELEVANT:
            self.logger.info(f"⏭️ Skipping {entry['keyword']} - Not Relevant")
            return None

        self.logger.info(f"🎨 Generating content for: {entry['keyword']} ({entry.get('category')})")
        prompts = self.get_content_prompts()
        generated_content = {
            'keyword': entry['keyword'],
            'category': entry.get('category'),
            'interest_score': entry.get('interest_score'),
            'generated_at': get_current_timestamp()
        }

        for content_type, prompt_template in prompts.items():
            prompt = prompt_template.format(
                category=entry.get('category', ''),
                keyword=entry['keyword'],
                reasoning=entry.get('ai_reasoning', '')
            )
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-4.1-nano",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                content_json = response.json()
                content_str = content_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                parsed_content = json.loads(content_str)
                generated_content[content_type] = parsed_content
                self.logger.info(f"✅ Generated {content_type}")
                add_delay('openai')
            except Exception as e:
                self.logger.error(f"❌ Error generating {content_type}: {str(e)}")
                generated_content[content_type] = {"error": str(e)}

        return generated_content

    def process_approved_entries(self, data):
        approved = [e for e in data if e.get('status') == settings.STATUS_RUN_GPT]
        if not approved:
            self.logger.warning("⚠️ No approved entries found (status = 'Run GPT')")
            return []

        self.logger.info(f"📊 Processing {len(approved)} approved entries for content generation")
        results = []
        for i, entry in enumerate(approved, 1):
            self.logger.info(f"\n🎯 Processing ({i}/{len(approved)}): {entry['keyword']}")
            content = self.generate_content_for_keyword(entry)
            if content:
                results.append(content)
        return results

    def update_original_data_with_content_links(self, original_data, generated_content):
        content_map = {item['keyword']: item for item in generated_content}
        updated = []
        for entry in original_data:
            key = entry['keyword']
            if key in content_map:
                # Mark Not Relevant entries explicitly
                if entry.get('category') == settings.CATEGORY_NOT_RELEVANT:
                    entry['status'] = 'Not Relevant'
                else:
                    entry['status'] = 'Content Generated'
                entry['content_generated_at'] = get_current_timestamp()
                # Replace drive:// with valid URLs for clickability (update base_url as needed)
                base_url = "https://your-public-host.com/ai-content"
                entry['instagram_link'] = f"{base_url}/instagram_{key.replace(' ', '_')}.txt"
                entry['blog_link'] = f"{base_url}/blog_{key.replace(' ', '_')}.html"
                entry['youtube_reel_link'] = f"{base_url}/reel_{key.replace(' ', '_')}.txt"
                entry['youtube_thumbnail_link'] = f"{base_url}/thumbnail_{key.replace(' ', '_')}.png"
                self.logger.info(f"📋 Updated {key} with content links")
            updated.append(entry)
        return updated

    def run(self):
        self.logger.info("🚀 Starting Phase 3: GPT-2 Content Generation")
        self.logger.info("=" * 60)

        try:
            data = load_data_from_csv('phase2_approved.csv')
            self.logger.info(f"📊 Loaded {len(data)} entries from phase2_approved.csv")

            generated_content = self.process_approved_entries(data)
            if not generated_content:
                self.logger.warning("⚠️ No content generated, please check 'Run GPT' status entries")
                return False

            save_json(generated_content, 'generated_content.json')

            summary = []
            for item in generated_content:
                instagram = item.get('instagram_post', {})
                blog = item.get('blog_article', {})
                summary.append({
                    'keyword': item['keyword'],
                    'category': item['category'],
                    'instagram_caption_preview': instagram.get('caption', '')[:100] + '...' if instagram.get('caption') else '',
                    'blog_title': blog.get('title', ''),
                    'generated_at': item.get('generated_at', ''),
                    'content_status': "Generated"
                })

            save_data_to_csv(summary, 'content_summary.csv', 'output')

            updated_data = self.update_original_data_with_content_links(data, generated_content)
            save_data_to_csv(updated_data, 'updated_trends_data.csv')

            self.logger.info("\n✅ Phase 3 Completed Successfully")
            self.logger.info(f"Generated content for {len(generated_content)} entries")
            self.logger.info("Saved generated content to JSON and CSV summary files")

            return True
        except Exception as e:
            self.logger.error(f"❌ Phase 3 Failed: {str(e)}")
            return False


def main():
    config_errors = settings.validate_config()
    if config_errors:
        print("❌ Configuration errors:")
        for err in config_errors:
            print(f"   {err}")
        return
    agent = GPT2ContentGenerationAgent()
    success = agent.run()
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
