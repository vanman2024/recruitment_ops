#!/usr/bin/env python3
"""
Diagnose what's being extracted from questionnaire
"""

import sys
import os
import json
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer

def diagnose_extraction():
    """Show raw extraction data"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    analyzer = VisionQuestionnaireAnalyzer(gemini_key)
    
    print("=" * 70)
    print("QUESTIONNAIRE EXTRACTION DIAGNOSTICS")
    print("=" * 70)
    
    # Analyze questionnaire
    result = analyzer.analyze_questionnaire_images('/home/gotime2022/recruitment_ops/questionnaire_images')
    
    print("\n1. RAW RESPONSES FOUND:")
    print("-" * 50)
    
    if result.get('responses'):
        for key, value in result['responses'].items():
            print(f"\n{key}:")
            print(f"  Question: {value.get('question', 'N/A')}")
            print(f"  Selections: {value.get('selections', [])}")
            print(f"  Text: {value.get('text', [])}")
            print(f"  All Options: {value.get('all_options', [])}")
    else:
        print("No responses found!")
    
    print("\n\n2. EQUIPMENT ANALYSIS:")
    print("-" * 50)
    
    if result.get('equipment_analysis'):
        equip = result['equipment_analysis']
        print(f"Brands Available: {equip.get('brands_available', [])}")
        print(f"Brands Selected: {equip.get('brands_selected', [])}")
        print(f"Equipment Types Available: {equip.get('equipment_types_available', [])}")
        print(f"Equipment Types Selected: {equip.get('equipment_types_selected', [])}")
    
    print("\n\n3. RAW PAGE ANALYSES:")
    print("-" * 50)
    
    if result.get('page_analyses'):
        for i, page in enumerate(result['page_analyses']):
            print(f"\nPage {i+1} - {page.get('page', 'unknown')}:")
            analysis = page.get('analysis', {})
            questions = analysis.get('questions_and_responses', [])
            print(f"  Questions found: {len(questions)}")
            
            for q in questions:
                print(f"\n  Question {q.get('question_number')}:")
                print(f"    Text: {q.get('question_text', 'N/A')[:100]}...")
                print(f"    Type: {q.get('response_type')}")
                print(f"    Selections: {q.get('actual_selections', [])}")
                
                # Check for equipment data
                equip_data = q.get('equipment_specific', {})
                if equip_data.get('is_equipment_question'):
                    print(f"    EQUIPMENT QUESTION!")
                    print(f"    Brands shown: {equip_data.get('equipment_brands_shown', [])}")
                    print(f"    Brands selected: {equip_data.get('equipment_brands_selected', [])}")
    
    # Save full result for inspection
    with open('questionnaire_diagnostic.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n\nFull diagnostic data saved to: questionnaire_diagnostic.json")

if __name__ == "__main__":
    diagnose_extraction()