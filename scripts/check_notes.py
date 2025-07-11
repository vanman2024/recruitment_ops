#!/usr/bin/env python3
"""
Check the notes that were saved to CATS
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv('/home/gotime2022/recruitment_ops/.env')

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient

def check_notes(candidate_id: int):
    """Get and display candidate notes"""
    
    client = CATSClient()
    candidate = client.get_candidate_details(candidate_id)
    
    if candidate:
        print(f"Candidate: {candidate.get('first_name')} {candidate.get('last_name')}")
        print("\n" + "="*60)
        print("CURRENT NOTES IN CATS:")
        print("="*60)
        print(candidate.get('notes', 'No notes found'))
    else:
        print("Candidate not found")

if __name__ == "__main__":
    check_notes(409281807)