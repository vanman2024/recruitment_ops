#!/usr/bin/env python3
"""Show complete extraction results from Claude 4 Opus"""

import os
import sys
import json
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.comprehensive_attachment_processor import ComprehensiveAttachmentProcessor

def show_extraction_results():
    """Show what Claude 4 Opus extracts from the questionnaire"""
    
    pdf_path = '/mnt/c/Users/angel/Downloads/Recruiting - Dayforce (1).pdf'
    if not os.path.exists(pdf_path):
        print(f"PDF not found at: {pdf_path}")
        return
    
    print("CLAUDE 4 OPUS - COMPLETE EXTRACTION RESULTS")
    print("=" * 60)
    
    processor = ComprehensiveAttachmentProcessor()
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Convert PDF
        temp_pdf = os.path.join(temp_dir, 'dayforce.pdf')
        shutil.copy(pdf_path, temp_pdf)
        processor._convert_pdf_to_images(temp_pdf, temp_dir)
        
        # Analyze with Claude 4 Opus
        result = processor.vision_analyzer.analyze_questionnaire_images(temp_dir)
        
        # Show complete extraction
        if 'candidate_profile' in result:
            profile = result['candidate_profile']
            
            print("\n📋 CANDIDATE PROFILE EXTRACTED:")
            print("-" * 60)
            print(json.dumps(profile, indent=2))
        
        # Show all questions and responses
        print("\n\n📝 ALL QUESTIONS AND RESPONSES:")
        print("-" * 60)
        
        if 'page_analyses' in result:
            question_count = 0
            for page_data in result['page_analyses']:
                page_analysis = page_data.get('analysis', {})
                if 'questions_and_responses' in page_analysis:
                    for q in page_analysis['questions_and_responses']:
                        question_count += 1
                        print(f"\nQ{q.get('question_number', question_count)}: {q.get('question_text', '')}")
                        print(f"Type: {q.get('question_type', '')}")
                        print(f"Options: {q.get('all_available_options', [])}")
                        print(f"SELECTED: {q.get('actual_selections', [])}")
                        
                        # Show equipment info if relevant
                        equipment = q.get('equipment_specific', {})
                        if equipment.get('is_equipment_question'):
                            print(f"Equipment Brands: {equipment.get('equipment_brands_selected', [])}")
                            print(f"Equipment Types: {equipment.get('equipment_types_selected', [])}")
        
        # Summary
        print("\n\n✅ EXTRACTION SUMMARY:")
        print("-" * 60)
        
        # Count what was extracted
        certifications = profile.get('certifications', {})
        equipment = profile.get('equipment_experience', {})
        preferences = profile.get('work_preferences', {})
        
        print(f"Certifications detected: {len([v for v in certifications.values() if v])}")
        print(f"Equipment brands: {len(equipment.get('brands_worked_with', []))}")
        print(f"Equipment types: {len(equipment.get('equipment_types', []))}")
        print(f"Work preferences: {len([v for v in preferences.values() if v])}")
        print(f"Total questions processed: {question_count}")
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    show_extraction_results()