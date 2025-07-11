#!/usr/bin/env python3
"""
Debug the extraction flow to see where data is lost
"""

import sys
import os
import json
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
from catsone.processors.dynamic_extraction_system import DynamicExtractionSystem

def debug_extraction():
    """Debug extraction flow"""
    
    print("=" * 70)
    print("DEBUGGING EXTRACTION FLOW")
    print("=" * 70)
    
    # Step 1: Analyze questionnaire
    gemini_key = os.getenv('GEMINI_API_KEY')
    analyzer = VisionQuestionnaireAnalyzer(gemini_key)
    
    print("\n1. Running Vision Analysis...")
    vision_result = analyzer.analyze_questionnaire_images('/home/gotime2022/recruitment_ops/questionnaire_images')
    
    # Check what we got
    print("\n2. Vision Result Structure:")
    print(f"   - Has 'responses': {'responses' in vision_result}")
    print(f"   - Has 'equipment_analysis': {'equipment_analysis' in vision_result}")
    print(f"   - Has 'candidate_profile': {'candidate_profile' in vision_result}")
    
    if 'equipment_analysis' in vision_result:
        equip = vision_result['equipment_analysis']
        print(f"\n   Equipment Analysis:")
        print(f"   - Brands available: {equip.get('brands_available', [])}")
        print(f"   - Brands selected: {equip.get('brands_selected', [])}")
        print(f"   - Equipment types: {equip.get('equipment_types_selected', [])}")
    
    # Step 2: Extract data
    print("\n\n3. Running Dynamic Extraction...")
    extractor = DynamicExtractionSystem()
    extracted_data = extractor.extract_all_questionnaire_data(vision_result)
    
    print("\n4. Extracted Data:")
    print(f"   - Equipment brands selected: {extracted_data['equipment']['brands_selected']}")
    print(f"   - Equipment brands available: {extracted_data['equipment']['brands_available']}")
    print(f"   - Certifications: {list(extracted_data['certifications'].keys())}")
    
    # Check certifications in detail
    print("\n5. Certification Details:")
    for cert_key, cert_data in extracted_data['certifications'].items():
        print(f"   - {cert_key}: {cert_data.get('answer', 'N/A')}")
    
    # Step 3: Format for role
    print("\n\n6. Formatting for Heavy Equipment Technician Role...")
    
    # Add candidate info
    extracted_data['candidate_info'] = {
        'name': 'Gaétan Desrochers',
        'location': '',
        'candidate_id': 399702647
    }
    
    formatted_notes = extractor.format_for_role(
        all_data=extracted_data,
        role_type='heavy_equipment_technician',
        custom_requirements={}
    )
    
    print("\n7. FINAL FORMATTED NOTES:")
    print("-" * 70)
    print(formatted_notes)
    print("-" * 70)
    
    # Save debug data
    debug_data = {
        'vision_result': vision_result,
        'extracted_data': extracted_data,
        'formatted_notes': formatted_notes
    }
    
    with open('extraction_debug.json', 'w') as f:
        json.dump(debug_data, f, indent=2)
    
    print("\n\nDebug data saved to: extraction_debug.json")

if __name__ == "__main__":
    debug_extraction()