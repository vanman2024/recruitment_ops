#!/usr/bin/env python3
"""
Debug what Claude is extracting from the questionnaire
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv('/home/gotime2022/recruitment_ops/.env')

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.comprehensive_attachment_processor import ComprehensiveAttachmentProcessor

def debug_extraction(candidate_id: int):
    """Debug questionnaire extraction"""
    
    processor = ComprehensiveAttachmentProcessor()
    
    print("Processing attachments...")
    result = processor.process_all_attachments(candidate_id)
    
    print("\n" + "="*60)
    print("ATTACHMENT PROCESSING RESULTS")
    print("="*60)
    
    # Show what was found
    print(f"\nAttachments found: {result.get('attachments_found', 0)}")
    print(f"Resume data available: {'Yes' if result.get('resume_data') else 'No'}")
    print(f"Questionnaire data available: {'Yes' if result.get('questionnaire_data') else 'No'}")
    
    # Show questionnaire data structure
    if result.get('questionnaire_data'):
        q_data = result['questionnaire_data']
        print("\n" + "-"*40)
        print("QUESTIONNAIRE DATA STRUCTURE:")
        print("-"*40)
        
        # Show top-level keys
        print(f"Top-level keys: {list(q_data.keys())}")
        
        # Check for candidate profile
        if 'candidate_profile' in q_data:
            profile = q_data['candidate_profile']
            print(f"\nCandidate profile keys: {list(profile.keys()) if isinstance(profile, dict) else 'NOT A DICT'}")
            
            # Show all_responses count
            if isinstance(profile, dict) and 'all_responses' in profile:
                responses = profile['all_responses']
                print(f"\nTotal responses extracted: {len(responses)}")
                
                # Show first few responses
                print("\nFirst 5 responses:")
                for i, resp in enumerate(responses[:5]):
                    print(f"\n{i+1}. Question: {resp.get('question_text', 'N/A')[:100]}...")
                    print(f"   Selections: {resp.get('actual_selections', [])}")
        
        # Save full data for inspection
        with open('questionnaire_debug.json', 'w') as f:
            json.dump(q_data, f, indent=2)
        print("\n✅ Full questionnaire data saved to questionnaire_debug.json")

if __name__ == "__main__":
    debug_extraction(409281807)