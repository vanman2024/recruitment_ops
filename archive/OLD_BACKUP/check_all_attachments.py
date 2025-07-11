#!/usr/bin/env python3
"""
Check all attachments for a candidate
"""

import sys
import os
import requests
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient

def check_all_attachments(candidate_id):
    """Get all attachments for a candidate"""
    
    cats = CATSClient()
    
    try:
        # Get all attachments
        url = f"{cats.base_url}/candidates/{candidate_id}/attachments"
        response = requests.get(url, headers=cats.headers)
        
        if response.status_code == 200:
            data = response.json()
            attachments = data.get('_embedded', {}).get('attachments', [])
            
            print(f"\nFound {len(attachments)} attachments for candidate {candidate_id}:")
            print("-" * 60)
            
            for i, attachment in enumerate(attachments):
                print(f"\n{i+1}. {attachment.get('filename')}")
                print(f"   ID: {attachment.get('id')}")
                print(f"   Type: {'Resume' if attachment.get('is_resume') else 'Other'}")
                print(f"   Created: {attachment.get('created_at')}")
                print(f"   Size: {attachment.get('file_size', 'Unknown')} bytes")
                if attachment.get('description'):
                    print(f"   Description: {attachment.get('description')}")
                
            return attachments
        else:
            print(f"Error getting attachments: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    candidate_id = 399702647
    
    print("=" * 60)
    print(f"CHECKING ALL ATTACHMENTS FOR CANDIDATE {candidate_id}")
    print("=" * 60)
    
    attachments = check_all_attachments(candidate_id)
    
    # Check for questionnaire images
    print("\n\nChecking local questionnaire images:")
    print("-" * 60)
    
    questionnaire_path = '/home/gotime2022/recruitment_ops/questionnaire_images'
    if os.path.exists(questionnaire_path):
        files = sorted(os.listdir(questionnaire_path))
        print(f"Found {len(files)} files in {questionnaire_path}:")
        for f in files:
            file_path = os.path.join(questionnaire_path, f)
            size = os.path.getsize(file_path)
            print(f"  • {f} ({size:,} bytes)")
    else:
        print(f"Directory not found: {questionnaire_path}")

if __name__ == "__main__":
    main()