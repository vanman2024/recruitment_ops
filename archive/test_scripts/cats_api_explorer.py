#!/usr/bin/env python3
"""
Explore CATS API to understand how attachments/documents work
"""

import sys
import requests
import json
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient

def explore_cats_api():
    """Explore different CATS API endpoints to find attachment handling"""
    
    cats = CATSClient()
    candidate_id = 399702647
    
    print("=== EXPLORING CATS API ENDPOINTS ===")
    print(f"Base URL: {cats.base_url}")
    print(f"Candidate ID: {candidate_id}")
    
    # Test different endpoints
    endpoints_to_test = [
        f"/candidates/{candidate_id}",
        f"/candidates/{candidate_id}/attachments", 
        f"/candidates/{candidate_id}/documents",
        f"/candidates/{candidate_id}/files",
        f"/attachments",
        f"/documents",
        f"/files"
    ]
    
    for endpoint in endpoints_to_test:
        full_url = cats.base_url + endpoint
        print(f"\n--- Testing: {endpoint} ---")
        
        try:
            response = requests.get(full_url, headers=cats.headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Look for attachment-related fields
                if isinstance(data, dict):
                    for key, value in data.items():
                        if any(keyword in key.lower() for keyword in ['attach', 'file', 'document', 'resume']):
                            print(f"  Found {key}: {type(value)} - {value if not isinstance(value, (list, dict)) else f'{len(value)} items' if isinstance(value, list) else 'dict'}")
                            
                            if isinstance(value, list) and value:
                                print(f"    Sample item: {list(value[0].keys()) if isinstance(value[0], dict) else value[0]}")
                
                # Check _embedded for attachments
                if '_embedded' in data:
                    embedded = data['_embedded']
                    print(f"  _embedded keys: {list(embedded.keys())}")
                    
                    for key, value in embedded.items():
                        if any(keyword in key.lower() for keyword in ['attach', 'file', 'document']):
                            print(f"    Found in _embedded - {key}: {len(value) if isinstance(value, list) else type(value)}")
                            if isinstance(value, list) and value:
                                print(f"      Sample: {value[0]}")
                
            elif response.status_code == 404:
                print("  Not found")
            else:
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Exception: {e}")
    
    # Also try to get candidate details and dump full structure
    print(f"\n--- FULL CANDIDATE DETAILS ---")
    try:
        candidate = cats.get_candidate_details(candidate_id)
        if candidate:
            print("Full candidate data structure:")
            print(json.dumps(candidate, indent=2)[:2000] + "..." if len(json.dumps(candidate)) > 2000 else json.dumps(candidate, indent=2))
        else:
            print("Could not get candidate details")
    except Exception as e:
        print(f"Error getting candidate details: {e}")

def check_api_documentation():
    """Check if we can find API documentation endpoints"""
    
    cats = CATSClient()
    
    print(f"\n=== CHECKING API DOCUMENTATION ===")
    
    # Common API documentation endpoints
    doc_endpoints = [
        f"{cats.base_url}/",
        f"{cats.base_url}/docs",
        f"{cats.base_url}/swagger",
        f"{cats.base_url}/api-docs",
        f"https://api.catsone.com/v3/",
        f"https://api.catsone.com/docs"
    ]
    
    for endpoint in doc_endpoints:
        print(f"\nTrying: {endpoint}")
        try:
            response = requests.get(endpoint, headers=cats.headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"Content-Type: {content_type}")
                
                if 'json' in content_type:
                    data = response.json()
                    print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                elif 'html' in content_type:
                    print("HTML response (documentation page?)")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    explore_cats_api()
    check_api_documentation()