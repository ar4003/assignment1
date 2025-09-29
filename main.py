"""
Main Execution Script for AI Social Media Automation
Coordinates all phases of the automation workflow
"""

import sys
import os
import argparse
from datetime import datetime
import logging

# Add current directory to path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from scripts.utils import setup_logging, create_sample_data, save_data_to_csv


class AIAutomationOrchestrator:
    """Main orchestrator for AI Social Media Automation"""
    
    def __init__(self):
        self.logger = setup_logging(settings.LOG_LEVEL)
        
    def display_banner(self):
        """Display application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     AI SOCIAL MEDIA AUTOMATION SYSTEM                      ║
║                       Assignment 1 - Complete Solution                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Based on Assignment 1 Video Requirements")
        print("=" * 80)
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        
        self.logger.info("🔍 Checking prerequisites...")
        
        # Validate configuration
        config_errors = settings.validate_config()
        if config_errors:
            self.logger.error("❌ Configuration errors found:")
            for error in config_errors:
                self.logger.error(f"   {error}")
            return False
        
        self.logger.info("✅ All prerequisites satisfied")
        return True
    
    def run_phase1(self):
        """Run Phase 1: Google Trends Extraction"""
        
        self.logger.info("\n🚀 PHASE 1: Google Trends Data Extraction")
        self.logger.info("=" * 60)
        
        try:
            from scripts.phase1_google_trends import ImprovedGoogleTrendsExtractor
            extractor = ImprovedGoogleTrendsExtractor()
            data = extractor.extract_trending_data()
            success = extractor.save_to_csv(data)

            
            
            
            if success:
                self.logger.info("✅ Phase 1 completed successfully")
                return True
            else:
                self.logger.error("❌ Phase 1 failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in Phase 1: {str(e)}")
            return False
    
    def run_phase2(self):
        """Run Phase 2: GPT-1 Categorization"""
        
        self.logger.info("\n🚀 PHASE 2: GPT-1 Agent Categorization")
        self.logger.info("=" * 60)
        
        try:
            from scripts.phase2_gpt1_categorization import GPT1CategorizationAgent
            
            agent = GPT1CategorizationAgent()
            success = agent.run()
            
            if success:
                self.logger.info("✅ Phase 2 completed successfully")
                return True
            else:
                self.logger.error("❌ Phase 2 failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in Phase 2: {str(e)}")
            return False
    
    def run_phase3(self):
        """Run Phase 3: GPT-2 Content Generation"""
        
        self.logger.info("\n🚀 PHASE 3: GPT-2 Content Generation")
        self.logger.info("=" * 60)
        
        try:
            from scripts.phase3_gpt2_content_generation import GPT2ContentGenerationAgent
            
            agent = GPT2ContentGenerationAgent()
            success = agent.run()
            
            if success:
                self.logger.info("✅ Phase 3 completed successfully")
                return True
            else:
                self.logger.error("❌ Phase 3 failed - this is normal if no entries are approved")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in Phase 3: {str(e)}")
            return False
    
    def run_phase4(self):
        """Run Phase 4: Google Sheets Integration"""
        
        self.logger.info("\n🚀 PHASE 4: Google Sheets Integration")
        self.logger.info("=" * 60)
        
        try:
            from scripts.phase4_sheets_integration import GoogleSheetsIntegration
            
            integration = GoogleSheetsIntegration()
            success = integration.run()
            
            if success:
                self.logger.info("✅ Phase 4 completed successfully")
                return True
            else:
                self.logger.error("❌ Phase 4 failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in Phase 4: {str(e)}")
            return False
    
    def create_sample_data_if_needed(self):
        """Create sample data for testing if no real data available"""
        
        self.logger.info("\n🧪 Creating sample data for testing...")
        
        sample_data = create_sample_data()
        filepath = save_data_to_csv(sample_data, 'sample_trends_data.csv')
        
        self.logger.info(f"📊 Created sample data: {filepath}")
        self.logger.info("💡 You can use this for testing the workflow")
        
        return True
    
    def run_all_phases(self):
        """Run all automated phases"""
        
        self.display_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.logger.error("❌ Prerequisites not satisfied. Please fix configuration.")
            return False
        
        # Track completed phases
        completed_phases = 0
        total_phases = 4
        
        # Phase 1: Google Trends Extraction
        if self.run_phase1():
            completed_phases += 1
        else:
            self.logger.warning("⚠️ Phase 1 failed - creating sample data for testing")
            self.create_sample_data_if_needed()
            # Don't return False, continue with sample data
        
        # Phase 2: GPT-1 Categorization
        if self.run_phase2():
            completed_phases += 1
        else:
            self.logger.error("❌ Stopping at Phase 2 failure")
            return False
        
        # Phase 3: GPT-2 Content Generation (might fail if no approved items)
        if self.run_phase3():
            completed_phases += 1
        else:
            self.logger.info("ℹ️ Phase 3: No content generated (normal if no entries approved)")
        
        # Phase 4: Google Sheets Integration
        if self.run_phase4():
            completed_phases += 1
        
        # Display results
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🏁 EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"✅ Completed {completed_phases}/{total_phases} phases")
        
        if completed_phases >= 2:  # At least extraction and categorization
            self.logger.info("🎉 Core automation phases completed!")
            self.logger.info("\n💡 MANUAL WORKFLOW INSTRUCTIONS:")
            self.logger.info("   1. 📊 Open your Google Sheets")
            self.logger.info("   2. 📝 Review categorized keywords") 
            self.logger.info("   3. ✅ For approved items: Change Status from 'Pending' to 'Run GPT'")
            self.logger.info("   4. 🎨 Run Phase 3 again to generate content")
            self.logger.info("   5. 📝 Review generated content")
            self.logger.info("   6. 📱 For publishing: Change Status to 'Post Live'")
        else:
            self.logger.error("❌ Core phases failed. Check configuration and try again.")
        
        self.logger.info(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return completed_phases >= 2


def main():
    """Main function with command-line interface"""
    
    parser = argparse.ArgumentParser(description='AI Social Media Automation System')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3, 4], 
                       help='Run specific phase (1-4)')
    parser.add_argument('--sample', action='store_true', 
                       help='Create sample data for testing')
    
    args = parser.parse_args()
    
    orchestrator = AIAutomationOrchestrator()
    
    if args.sample:
        orchestrator.create_sample_data_if_needed()
        return
    
    if args.phase:
        # Run specific phase
        if args.phase == 1:
            success = orchestrator.run_phase1()
        elif args.phase == 2:
            success = orchestrator.run_phase2()
        elif args.phase == 3:
            success = orchestrator.run_phase3()
        elif args.phase == 4:
            success = orchestrator.run_phase4()
        
        if not success:
            exit(1)
    else:
        # Run all phases
        success = orchestrator.run_all_phases()
        if not success:
            exit(1)


if __name__ == "__main__":
    main()
