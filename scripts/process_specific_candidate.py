#!/usr/bin/env python3
"""
Process a specific candidate by ID
Useful for testing or manual processing
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/gotime2022/recruitment_ops/.env')

# Add project to path
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

CATS_API_KEY = os.getenv('CATS_API_KEY')
CATS_API_URL = "https://api.catsone.com/v3"
headers = {"Authorization": f"Token {CATS_API_KEY}"}

def check_and_process_candidate(candidate_id):
    """Check candidate tags and process if has questionnaire tag"""
    
    print(f"Checking candidate {candidate_id}...")
    
    # Get candidate details
    url = f"{CATS_API_URL}/candidates/{candidate_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error getting candidate: {response.status_code}")
        return False
    
    candidate = response.json()
    name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
    print(f"Found: {name}")
    
    # Get tags
    tags_url = f"{CATS_API_URL}/candidates/{candidate_id}/tags"
    tags_response = requests.get(tags_url, headers=headers, params={"page": 1, "per_page": 100})
    
    if tags_response.status_code == 200:
        tags = tags_response.json().get('_embedded', {}).get('tags', [])
        tag_names = [tag.get('title', '') for tag in tags]
        
        print(f"\nTags: {tag_names}")
        
        if "Questionnaire Completed" in tag_names:
            print("✅ Has 'Questionnaire Completed' tag!")
            
            # Get pipelines
            pipelines_url = f"{CATS_API_URL}/candidates/{candidate_id}/pipelines"
            pipelines_response = requests.get(pipelines_url, headers=headers)
            
            if pipelines_response.status_code == 200:
                pipelines = pipelines_response.json().get('_embedded', {}).get('pipelines', [])
                
                if pipelines:
                    # Process with first active pipeline
                    for pipeline in pipelines:
                        if not pipeline.get('archived', False):
                            job_id = pipeline.get('job_id')
                            if job_id:
                                print(f"\nProcessing for job {job_id}...")
                                
                                processor = IntelligentCandidateProcessor()
                                result = processor.process_candidate_for_job(candidate_id, job_id)
                                
                                if result.get('success'):
                                    print("✅ Successfully processed!")
                                    
                                    # Add processed tag
                                    add_tag_url = f"{CATS_API_URL}/candidates/{candidate_id}/tags"
                                    tag_data = {"tags": [{"title": "ai_notes_generated"}]}
                                    requests.put(add_tag_url, headers=headers, json=tag_data)
                                    
                                    return True
                                else:
                                    print(f"❌ Processing failed: {result.get('error')}")
                                break
                else:
                    print("❌ No pipelines found")
            else:
                print(f"❌ Error getting pipelines: {pipelines_response.status_code}")
        else:
            print("❌ Does not have 'Questionnaire Completed' tag")
    else:
        print(f"❌ Error getting tags: {tags_response.status_code}")
    
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('candidate_id', type=int, help='Candidate ID to process')
    args = parser.parse_args()
    
    check_and_process_candidate(args.candidate_id)