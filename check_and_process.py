#!/usr/bin/env python3
"""
Check for candidates with the questionnaire tag and process them
Run this periodically (cron job) or manually
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient

def check_for_tagged_candidates():
    """Find all candidates with 'Questionnaire Completed' tag"""
    
    client = CATSClient()
    api_key = os.getenv('CATS_API_KEY')
    
    # Get all candidates (you might want to filter by date)
    url = f"{client.base_url}/candidates?per_page=100&sort=-date_modified"
    headers = {"Authorization": f"Token {api_key}", "Accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error getting candidates: {response.status_code}")
        return []
    
    candidates = response.json().get('_embedded', {}).get('candidates', [])
    tagged_candidates = []
    
    # Check each candidate for the tag
    for candidate in candidates:
        candidate_id = candidate['id']
        
        # Get tags for this candidate
        tags_url = f"{client.base_url}/candidates/{candidate_id}/tags"
        tags_response = requests.get(tags_url, headers=headers)
        
        if tags_response.status_code == 200:
            tags_data = tags_response.json()
            tags = tags_data.get('_embedded', {}).get('tags', [])
            
            # Check for questionnaire completed tag
            for tag in tags:
                if 'questionnaire completed' in tag.get('title', '').lower():
                    # Check if already processed (by looking at notes)
                    if not candidate.get('notes') or len(candidate.get('notes', '')) < 100:
                        tagged_candidates.append({
                            'id': candidate_id,
                            'name': f"{candidate['first_name']} {candidate['last_name']}",
                            'tag': tag['title']
                        })
                    break
    
    return tagged_candidates

def process_candidates(candidates):
    """Process each candidate"""
    from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor
    
    processor = IntelligentCandidateProcessor()
    
    for candidate in candidates:
        print(f"\nProcessing {candidate['name']} (ID: {candidate['id']})")
        
        # Get job ID - using default for now
        job_id = 16702578  # You could make this smarter
        
        try:
            result = processor.process_candidate_for_job(candidate['id'], job_id)
            if result.get('success'):
                print(f"✅ Successfully processed {candidate['name']}")
            else:
                print(f"❌ Failed to process: {result.get('error')}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print(f"Checking for candidates with questionnaire tag at {datetime.now()}")
    
    candidates = check_for_tagged_candidates()
    
    if candidates:
        print(f"\nFound {len(candidates)} candidates to process:")
        for c in candidates:
            print(f"  - {c['name']} (ID: {c['id']})")
        
        print("\nStarting processing...")
        process_candidates(candidates)
    else:
        print("No unprocessed candidates with questionnaire tag found.")
    
    print("\nDone!")