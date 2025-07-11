#!/usr/bin/env python3
"""Debug why candidate isn't being found"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, '.env'))

CATS_API_KEY = os.getenv('CATS_API_KEY')
CATS_API_URL = "https://api.catsone.com/v3"
headers = {"Authorization": f"Token {CATS_API_KEY}"}

# Check specific candidate
candidate_id = 398063905
print(f"Checking candidate {candidate_id}...")

# Get candidate details
response = requests.get(f"{CATS_API_URL}/candidates/{candidate_id}", headers=headers)
if response.status_code == 200:
    candidate = response.json()
    print(f"Name: {candidate.get('first_name')} {candidate.get('last_name')}")
    print(f"Updated: {candidate.get('updated_at')}")
else:
    print(f"Error getting candidate: {response.status_code}")

# Get tags
tag_response = requests.get(f"{CATS_API_URL}/candidates/{candidate_id}/tags", headers=headers)
if tag_response.status_code == 200:
    tag_data = tag_response.json()
    if '_embedded' in tag_data:
        tags = [tag['title'] for tag in tag_data['_embedded'].get('tags', [])]
        print(f"\nTags: {tags}")
        print(f"Has 'Questionnaire Completed': {'Questionnaire Completed' in tags}")
        print(f"Has 'AI Notes Generated': {'AI Notes Generated' in tags}")
        
        if 'Questionnaire Completed' in tags and 'AI Notes Generated' not in tags:
            print("\n✅ This candidate SHOULD be processed!")
        else:
            print("\n❌ This candidate should NOT be processed")

# Check if in cache
cache_file = os.path.join(project_root, 'logs', 'processed_candidates.json')
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        cache = json.load(f)
        if str(candidate_id) in cache:
            print(f"\n⚠️ WARNING: Candidate is in processed cache!")
            print("This prevents reprocessing even without the tag")

# Test the search that GitHub Actions uses
print("\n\nTesting search parameters...")
end_date = datetime.now()
start_date = end_date - timedelta(hours=48)
params = {
    "updated_after": start_date.isoformat(),
    "per_page": 100
}
print(f"Searching for candidates updated after: {start_date.isoformat()}")

search_response = requests.get(f"{CATS_API_URL}/candidates", headers=headers, params=params)
if search_response.status_code == 200:
    data = search_response.json()
    if '_embedded' in data:
        candidates = data['_embedded'].get('candidates', [])
        print(f"Found {len(candidates)} candidates in date range")
        
        # Look for our candidate
        found = False
        for c in candidates:
            if c.get('id') == candidate_id:
                found = True
                print(f"✅ Found candidate {candidate_id} in search results!")
                break
        
        if not found:
            print(f"❌ Candidate {candidate_id} NOT in search results")
            print("Possible reasons:")
            print("- Not updated in last 48 hours")
            print("- Different timezone issue")
            print("- API pagination (only checking first 100)")
else:
    print(f"Search error: {search_response.status_code}")