#!/usr/bin/env python3
"""
Enhanced questionnaire monitor that checks each candidate's tags
"""

import os
import sys
import time
import json
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, '.env'))

# Add project to path
sys.path.append(project_root)
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

# Setup logging
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'questionnaire_monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CATS_API_KEY = os.getenv('CATS_API_KEY')
CATS_API_URL = "https://api.catsone.com/v3"
POLL_INTERVAL = 300  # 5 minutes
QUESTIONNAIRE_TAG = "Questionnaire Completed"
PROCESSED_TAG = "ai_notes_generated"
CHECK_HOURS = 48  # Check candidates updated in last 48 hours

class EnhancedQuestionnaireMonitor:
    def __init__(self):
        self.headers = {"Authorization": f"Token {CATS_API_KEY}"}
        self.processor = IntelligentCandidateProcessor()
        self.processed_cache = self.load_cache()
    
    def load_cache(self):
        """Load processed candidates cache"""
        cache_file = os.path.join(project_root, 'logs', 'processed_candidates.json')
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return set(json.load(f))
            except:
                pass
        return set()
    
    def save_cache(self):
        """Save processed candidates cache"""
        cache_file = os.path.join(project_root, 'logs', 'processed_candidates.json')
        with open(cache_file, 'w') as f:
            json.dump(list(self.processed_cache), f)
    
    def get_candidate_tags(self, candidate_id):
        """Get all tags for a specific candidate"""
        url = f"{CATS_API_URL}/candidates/{candidate_id}/tags"
        params = {"page": 1, "per_page": 100}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                tags = data.get('_embedded', {}).get('tags', [])
                return [tag.get('title', '') for tag in tags]
            else:
                logger.debug(f"Could not get tags for candidate {candidate_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting tags for candidate {candidate_id}: {e}")
            return []
    
    def find_candidates_with_questionnaire(self):
        """Find candidates by checking each one's tags"""
        candidates_with_tag = []
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(hours=CHECK_HOURS)).strftime('%Y-%m-%d')
        
        logger.info(f"Searching for candidates updated since {since_date}")
        
        page = 1
        total_checked = 0
        
        while page <= 20:  # Max 20 pages (1000 candidates)
            url = f"{CATS_API_URL}/candidates"
            params = {
                "page": page,
                "per_page": 50,
                "sort": "-updated_at"  # Most recently updated first
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get('_embedded', {}).get('candidates', [])
                    
                    if not candidates:
                        break
                    
                    logger.info(f"Page {page}: Checking {len(candidates)} candidates...")
                    
                    for candidate in candidates:
                        candidate_id = candidate.get('id')
                        total_checked += 1
                        
                        # Skip if already processed
                        if str(candidate_id) in self.processed_cache:
                            continue
                        
                        # Get candidate's tags
                        tags = self.get_candidate_tags(candidate_id)
                        
                        # Check for questionnaire tag
                        if QUESTIONNAIRE_TAG in tags:
                            # Make sure doesn't already have processed tag
                            if PROCESSED_TAG not in tags:
                                name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
                                logger.info(f"  ✓ Found: {name} (ID: {candidate_id}) with '{QUESTIONNAIRE_TAG}' tag")
                                candidates_with_tag.append(candidate)
                        
                        # Small delay to avoid rate limits
                        if total_checked % 10 == 0:
                            time.sleep(0.5)
                    
                    page += 1
                else:
                    logger.error(f"Error getting candidates: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"Error searching candidates: {e}")
                break
        
        logger.info(f"Checked {total_checked} candidates, found {len(candidates_with_tag)} with questionnaire tag")
        return candidates_with_tag
    
    def add_tag_to_candidate(self, candidate_id, tag_name):
        """Add tag to candidate"""
        try:
            # First, get all tags to find the ID for our tag
            tags_url = f"{CATS_API_URL}/tags"
            response = requests.get(tags_url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get tags list: {response.status_code}")
                return False
            
            tags_data = response.json()
            tag_id = None
            
            # Find the tag ID
            if '_embedded' in tags_data:
                tags = tags_data['_embedded'].get('tags', [])
                for tag in tags:
                    if tag.get('title') == tag_name:
                        tag_id = tag.get('id')
                        logger.info(f"Found tag '{tag_name}' with ID: {tag_id}")
                        break
            
            if not tag_id:
                logger.error(f"Tag '{tag_name}' not found in CATS system. Please create it first.")
                return False
            
            # Now attach the tag to the candidate using PUT with tag IDs
            url = f"{CATS_API_URL}/candidates/{candidate_id}/tags"
            
            # First get current tags
            current_response = requests.get(url, headers=self.headers)
            current_tag_ids = []
            
            if current_response.status_code == 200:
                current_data = current_response.json()
                if '_embedded' in current_data:
                    current_tags = current_data['_embedded'].get('tags', [])
                    current_tag_ids = [t.get('id') for t in current_tags if t.get('id')]
            
            # Add our tag ID if not already present
            if tag_id not in current_tag_ids:
                current_tag_ids.append(tag_id)
            
            # PUT request with all tag IDs
            data = {"tags": current_tag_ids}
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Successfully added tag '{tag_name}' (ID: {tag_id}) to candidate {candidate_id}")
                return True
            else:
                logger.error(f"Error adding tag: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding tag: {e}")
            return False
    
    def process_candidate(self, candidate):
        """Process a single candidate"""
        candidate_id = candidate.get('id')
        name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
        
        logger.info(f"Processing candidate {candidate_id}: {name}")
        
        # Get pipelines for the candidate
        pipelines_url = f"{CATS_API_URL}/candidates/{candidate_id}/pipelines"
        
        try:
            response = requests.get(pipelines_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                pipelines = data.get('_embedded', {}).get('pipelines', [])
                
                if not pipelines:
                    logger.warning(f"No pipelines found for candidate {candidate_id}")
                    return False
                
                # Process for each active pipeline
                success = False
                for pipeline in pipelines:
                    if pipeline.get('archived', False):
                        continue
                    
                    job_id = pipeline.get('job_id')
                    if not job_id:
                        continue
                    
                    logger.info(f"Processing candidate {candidate_id} for job {job_id}")
                    
                    # Use the processor
                    result = self.processor.process_candidate_for_job(candidate_id, job_id)
                    
                    if result.get('success'):
                        logger.info(f"✅ Successfully processed candidate {candidate_id}")
                        success = True
                    else:
                        logger.error(f"❌ Failed: {result.get('error')}")
                
                if success:
                    # Mark as processed
                    self.processed_cache.add(str(candidate_id))
                    
                    # Add processed tag
                    self.add_tag_to_candidate(candidate_id, PROCESSED_TAG)
                    
                    return True
                
                return False
            else:
                logger.error(f"Error getting pipelines: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing candidate {candidate_id}: {e}")
            return False
    
    def run_cycle(self):
        """Run one monitoring cycle"""
        logger.info("=" * 60)
        logger.info("Starting monitoring cycle...")
        logger.info(f"Looking for tag: '{QUESTIONNAIRE_TAG}'")
        
        # Find candidates with questionnaire tag
        candidates = self.find_candidates_with_questionnaire()
        
        if not candidates:
            logger.info("No new candidates to process")
            return
        
        # Process each
        processed = 0
        for candidate in candidates:
            if self.process_candidate(candidate):
                processed += 1
            
            # Delay to avoid rate limits
            time.sleep(2)
        
        # Save cache
        self.save_cache()
        
        logger.info(f"Processed {processed}/{len(candidates)} candidates")
    
    def run_continuous(self):
        """Run continuous monitoring"""
        logger.info(f"Starting enhanced monitoring")
        logger.info(f"Polling every {POLL_INTERVAL} seconds")
        
        while True:
            try:
                self.run_cycle()
            except KeyboardInterrupt:
                logger.info("\nStopped by user")
                break
            except Exception as e:
                logger.error(f"Error in cycle: {e}")
            
            logger.info(f"Waiting {POLL_INTERVAL} seconds...")
            time.sleep(POLL_INTERVAL)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='Run once')
    parser.add_argument('--interval', type=int, default=300, help='Poll interval (seconds)')
    args = parser.parse_args()
    
    global POLL_INTERVAL
    POLL_INTERVAL = args.interval
    
    monitor = EnhancedQuestionnaireMonitor()
    
    if args.once:
        monitor.run_cycle()
    else:
        monitor.run_continuous()

if __name__ == "__main__":
    main()