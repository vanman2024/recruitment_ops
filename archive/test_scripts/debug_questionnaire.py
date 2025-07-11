#!/usr/bin/env python3
"""
Debug questionnaire data structure
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.comprehensive_attachment_processor import ComprehensiveAttachmentProcessor

# Check what questionnaire data looks like
processor = ComprehensiveAttachmentProcessor()
result = processor.process_all_attachments(409281807)

print("Attachment Results:")
print(f"Attachments found: {result['attachments_found']}")
print(f"\nQuestionnaire data keys: {list(result.get('questionnaire_data', {}).keys())}")

# Print the actual questionnaire data structure
if result.get('questionnaire_data'):
    print("\nQuestionnaire data structure:")
    # Don't print all responses, just the structure
    qdata = result['questionnaire_data']
    if 'candidate_profile' in qdata:
        print("- candidate_profile:")
        print(f"  - all_responses: {len(qdata['candidate_profile'].get('all_responses', []))} items")
        if qdata['candidate_profile'].get('all_responses'):
            print(f"  - First response: {qdata['candidate_profile']['all_responses'][0]}")
    
    if 'error' not in qdata:
        print("\nExtracted equipment:")
        if 'candidate_profile' in qdata:
            equipment = qdata['candidate_profile'].get('equipment_experience', {})
            print(f"- Brands: {equipment.get('brands_worked_with', [])}")
            print(f"- Types: {equipment.get('equipment_types', [])}") 
    else:
        print(f"\nError: {qdata.get('error')}")