#!/usr/bin/env python3
"""
Show what's in the questionnaire
"""

import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.comprehensive_attachment_processor import ComprehensiveAttachmentProcessor

print("Analyzing questionnaire...")
processor = ComprehensiveAttachmentProcessor()
result = processor.process_all_attachments(409281807)

if result.get('questionnaire_data'):
    qdata = result['questionnaire_data']
    
    if 'candidate_profile' in qdata:
        profile = qdata['candidate_profile']
        responses = profile.get('all_responses', [])
        
        print(f"\n=== QUESTIONNAIRE HAS {len(responses)} QUESTIONS ===\n")
        
        # Show each question and answer
        for i, resp in enumerate(responses[:10]):  # First 10
            print(f"Q{i+1}: {resp.get('question_text', 'Unknown')}")
            print(f"Type: {resp.get('question_type', 'Unknown')}")
            print(f"Answer: {resp.get('actual_selections', 'None')}")
            print("-" * 60)
            
        if len(responses) > 10:
            print(f"\n... and {len(responses) - 10} more questions\n")
            
        # Show what should be in notes
        print("\n=== KEY INFORMATION THAT SHOULD BE IN NOTES ===")
        
        # Industries
        for resp in responses:
            if 'industries' in resp.get('question_text', '').lower():
                print(f"\nIndustries: {resp.get('actual_selections', [])}")
                
        # Experience years
        for resp in responses:
            qt = resp.get('question_text', '').lower()
            if 'years' in qt and 'experience' in qt:
                print(f"{resp.get('question_text')}: {resp.get('actual_selections', [])}")
                
        # Equipment brands
        equipment_brands = []
        for resp in responses:
            if resp.get('equipment_specific', {}).get('is_equipment_question'):
                selections = resp.get('actual_selections', [])
                for sel in selections:
                    if any(brand in sel for brand in ['CAT', 'Hitachi', 'Komatsu', 'Liebherr', 'John Deere']):
                        equipment_brands.append(sel)
        
        if equipment_brands:
            print(f"\nEquipment Experience: {', '.join(set(equipment_brands))}")
            
        # Certifications
        for resp in responses:
            qt = resp.get('question_text', '').lower()
            if any(cert in qt for cert in ['red seal', 'journeyman', 'certification', 'license', 'qualitative fit']):
                print(f"\n{resp.get('question_text')}: {resp.get('actual_selections', [])}")
    else:
        print("No candidate profile found")
else:
    print("No questionnaire data found")