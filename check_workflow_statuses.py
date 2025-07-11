#!/usr/bin/env python3
"""
Check workflow statuses for pipeline
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

CATS_API_KEY = os.getenv('CATS_API_KEY')
CATS_API_URL = "https://api.catsone.com/v3"

def get_workflow_statuses(workflow_id):
    """Get statuses for a workflow"""
    url = f"{CATS_API_URL}/pipelines/workflows/{workflow_id}/statuses"
    headers = {"Authorization": f"Token {CATS_API_KEY}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        statuses = response.json().get('_embedded', {}).get('statuses', [])
        print(f"\nFound {len(statuses)} statuses for workflow {workflow_id}:")
        for status in statuses:
            print(f"  - {status.get('title', 'Unknown')} (ID: {status.get('id', 'Unknown')})")
        return statuses
    else:
        print(f"Error getting workflow statuses: {response.status_code}")
        print(f"Response: {response.text}")
        return []

if __name__ == "__main__":
    # From the pipeline data we saw: workflow_id = 5691190
    workflow_id = 5691190
    
    print("Workflow Status Check")
    print("=" * 50)
    
    statuses = get_workflow_statuses(workflow_id)
    
    # Look for questionnaire-related status
    print("\n🔍 Looking for questionnaire-related statuses:")
    for status in statuses:
        title = status.get('title', '').lower()
        if 'questionnaire' in title or 'question' in title:
            print(f"  ✓ Found: {status.get('title')} (ID: {status.get('id')})")