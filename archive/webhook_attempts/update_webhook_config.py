#!/usr/bin/env python3
"""
Update CATS webhook configuration to use pipeline status changes
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

CATS_API_KEY = os.getenv('CATS_API_KEY')
CATS_API_URL = "https://api.catsone.com/v3"

def list_webhooks():
    """List all current webhooks"""
    url = f"{CATS_API_URL}/webhooks"
    headers = {"Authorization": f"Token {CATS_API_KEY}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        webhooks = response.json().get('_embedded', {}).get('webhooks', [])
        print(f"\nFound {len(webhooks)} webhooks:")
        for webhook in webhooks:
            print(f"\nID: {webhook['id']}")
            print(f"URL: {webhook['url']}")
            print(f"Event: {webhook['event']}")
            print(f"Enabled: {webhook.get('enabled', True)}")
        return webhooks
    else:
        print(f"Error listing webhooks: {response.status_code}")
        return []

def create_pipeline_webhook():
    """Create webhook for pipeline status changes"""
    url = f"{CATS_API_URL}/webhooks"
    headers = {
        "Authorization": f"Token {CATS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    webhook_data = {
        "event": "pipeline.status_changed",
        "target_url": "https://cats.ngrok.app/webhook/pipeline"
    }
    
    response = requests.post(url, json=webhook_data, headers=headers)
    if response.status_code in [200, 201]:
        print(f"\n✅ Created pipeline webhook successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"\n❌ Error creating webhook: {response.status_code}")
        print(f"Response: {response.text}")

def get_pipeline_statuses():
    """Get all available pipeline statuses"""
    url = f"{CATS_API_URL}/statuses"
    headers = {"Authorization": f"Token {CATS_API_KEY}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        statuses = response.json().get('_embedded', {}).get('statuses', [])
        print(f"\nAvailable pipeline statuses:")
        for status in statuses:
            print(f"  - {status['name']} (ID: {status['id']})")
        return statuses
    else:
        print(f"Error getting statuses: {response.status_code}")
        return []

if __name__ == "__main__":
    print("CATS Webhook Configuration Tool")
    print("=" * 50)
    
    # List current webhooks
    webhooks = list_webhooks()
    
    # Show available statuses
    statuses = get_pipeline_statuses()
    
    # Create pipeline webhook
    print("\nCreating pipeline status change webhook...")
    create_pipeline_webhook()