#!/usr/bin/env python3
"""
Direct processing script you can run manually
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Trigger processing via webhook
webhook_url = "https://cats.ngrok.app/webhook/candidate"
data = {
    "event": "candidate.updated",
    "candidate_id": 409281807,
    "_embedded": {
        "candidate": {"id": 409281807}
    }
}

print("Triggering questionnaire processing...")
response = requests.post(webhook_url, json=data)
print(f"Response: {response.status_code} - {response.text}")

if response.status_code == 200:
    print("\n✅ Processing triggered! Check CATS notes in about 30 seconds.")
    print("\nTo check notes:")
    print("curl -s 'https://api.catsone.com/v3/candidates/409281807' -H 'Authorization: Token 23ff55bbce3778ac88d7efc0e21f56f2' | jq -r '.notes'")
else:
    print("\n❌ Failed to trigger processing")