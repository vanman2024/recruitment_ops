#!/usr/bin/env python3
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, '.env'))

CATS_API_KEY = os.getenv('CATS_API_KEY')
CATS_API_URL = "https://api.catsone.com/v3"

candidate_id = 398063905
headers = {"Authorization": f"Token {CATS_API_KEY}"}

# Get tags
tag_response = requests.get(
    f"{CATS_API_URL}/candidates/{candidate_id}/tags",
    headers=headers
)

if tag_response.status_code == 200:
    tag_data = tag_response.json()
    if '_embedded' in tag_data:
        tags = [tag['title'] for tag in tag_data['_embedded'].get('tags', [])]
        print(f"Candidate {candidate_id} tags: {tags}")
        
        if "ai_notes_generated" in tags:
            print("❌ Already has 'ai_notes_generated' tag - won't be processed again")
        else:
            print("✅ Missing 'ai_notes_generated' tag - will be processed")