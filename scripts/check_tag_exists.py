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
headers = {"Authorization": f"Token {CATS_API_KEY}"}

# Check if ai_notes_generated tag exists
print("Checking if 'ai_notes_generated' tag exists in CATS...")

response = requests.get(f"{CATS_API_URL}/tags", headers=headers)
if response.status_code == 200:
    data = response.json()
    if '_embedded' in data:
        tags = data['_embedded'].get('tags', [])
        
        # Look for our tag
        ai_tag = None
        for tag in tags:
            if tag.get('title') == 'ai_notes_generated':
                ai_tag = tag
                break
        
        if ai_tag:
            print(f"✅ Tag exists! ID: {ai_tag.get('id')}, Title: {ai_tag.get('title')}")
        else:
            print("❌ Tag 'ai_notes_generated' does NOT exist in CATS")
            print("You need to create this tag in CATS first!")
            print("\nExisting tags:")
            for tag in tags[:10]:
                print(f"  - {tag.get('title')} (ID: {tag.get('id')})")
else:
    print(f"Error: {response.status_code}")