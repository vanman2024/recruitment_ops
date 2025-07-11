#!/usr/bin/env python3
"""
Manual candidate processing script
Usage: python3 process_candidate.py <candidate_id> [job_id]
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging to file and console
from datetime import datetime
LOG_DIR = '/home/gotime2022/recruitment_ops/logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f'recruitment_ops_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler()
    ]
)

# Load environment
load_dotenv('/home/gotime2022/recruitment_ops/.env')

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor
from catsone.integration.cats_integration import CATSClient

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 process_candidate.py <candidate_id> [job_id]")
        sys.exit(1)
    
    candidate_id = int(sys.argv[1])
    job_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    # If no job_id provided, try to find it
    if not job_id:
        cats = CATSClient()
        # Get candidate's pipeline info
        import requests
        url = f"{cats.base_url}/candidates/{candidate_id}/pipelines"
        headers = {"Authorization": f"Token {os.getenv('CATS_API_KEY')}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            pipelines = response.json().get('_embedded', {}).get('pipelines', [])
            if pipelines:
                job_id = pipelines[0].get('job_id')
                print(f"Found job ID: {job_id}")
            else:
                print("No pipeline entries found. Using default job ID.")
                job_id = 16702578
        else:
            print("Could not get pipeline info. Using default job ID.")
            job_id = 16702578
    
    print(f"\nProcessing candidate {candidate_id} for job {job_id}...")
    print("=" * 60)
    
    processor = IntelligentCandidateProcessor()
    result = processor.process_candidate_for_job(candidate_id, job_id)
    
    if result.get('success'):
        print(f"\n✅ Successfully processed candidate!")
        print(f"Candidate: {result.get('candidate_name')}")
        print(f"Job: {result.get('job_title')}")
        print("\nNotes have been updated in CATS.")
        
        # Show a preview of the notes
        notes = result.get('notes', '')
        if notes:
            print("\nNotes preview:")
            print("-" * 60)
            print(notes[:500] + "..." if len(notes) > 500 else notes)
    else:
        print(f"\n❌ Processing failed: {result.get('error')}")

if __name__ == "__main__":
    main()