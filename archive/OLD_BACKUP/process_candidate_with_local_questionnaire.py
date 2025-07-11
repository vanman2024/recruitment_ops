#!/usr/bin/env python3
"""
Process candidate with local questionnaire images
"""

import sys
import os
import logging
from datetime import datetime

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
from catsone.processors.dynamic_extraction_system import DynamicExtractionSystem
from catsone.processors.job_requirements_extractor import JobRequirementsExtractor
from catsone.integration.cats_integration import CATSClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def process_with_local_questionnaire(candidate_id: int, job_id: int, questionnaire_folder: str):
    """Process candidate using local questionnaire images"""
    
    print("=" * 70)
    print("PROCESSING CANDIDATE WITH LOCAL QUESTIONNAIRE")
    print("=" * 70)
    
    cats = CATSClient()
    gemini_key = os.getenv('GEMINI_API_KEY')
    vision_analyzer = VisionQuestionnaireAnalyzer(gemini_key)
    extractor = DynamicExtractionSystem()
    job_extractor = JobRequirementsExtractor()
    
    try:
        # Step 1: Get job requirements
        logger.info(f"Getting job requirements for job {job_id}")
        job_data = cats.get_job_details(job_id)
        if not job_data:
            return {'error': 'Job not found'}
        
        job_requirements = job_extractor.extract_job_requirements(job_data)
        print(f"\n✓ Job: {job_requirements['source']['job_title']}")
        
        # Step 2: Get candidate info
        candidate = cats.get_candidate_details(candidate_id)
        if not candidate:
            return {'error': 'Candidate not found'}
        
        candidate_name = f"{candidate.get('first_name')} {candidate.get('last_name')}"
        print(f"✓ Candidate: {candidate_name}")
        
        # Step 3: Process CATS attachments (resume, etc)
        processor = IntelligentCandidateProcessor()
        attachment_results = processor.attachment_processor.process_all_attachments(candidate_id)
        
        print(f"\n📎 CATS Attachments: {attachment_results['attachments_found']} found")
        for log in attachment_results['processing_log']:
            print(f"  • {log}")
        
        # Step 4: Analyze local questionnaire
        print(f"\n📝 Analyzing questionnaire from: {questionnaire_folder}")
        questionnaire_result = vision_analyzer.analyze_questionnaire_images(questionnaire_folder)
        
        if 'error' in questionnaire_result:
            return {'error': f"Vision analysis failed: {questionnaire_result['error']}"}
        
        # Check what we got
        if questionnaire_result.get('responses'):
            print(f"  ✓ Found {len(questionnaire_result['responses'])} questions")
        
        # Step 5: Extract ALL data
        all_data = extractor.extract_all_questionnaire_data(questionnaire_result)
        
        # Add candidate info
        all_data['candidate_info'] = {
            'name': candidate_name,
            'location': f"{candidate.get('city', '')}, {candidate.get('state', '')}".strip(', '),
            'candidate_id': candidate_id
        }
        
        # Add resume and interview data if available
        if attachment_results.get('resume_data'):
            all_data['resume_data'] = attachment_results['resume_data']
        
        if attachment_results.get('interview_notes'):
            all_data['interview_notes'] = attachment_results['interview_notes']
        
        # Show extraction summary
        print("\n🔍 Extraction Summary:")
        if all_data.get('equipment', {}).get('brands_selected'):
            print(f"  • Equipment Brands: {', '.join(all_data['equipment']['brands_selected'])}")
        
        if all_data.get('certifications'):
            certs = [k for k, v in all_data['certifications'].items() if v == 'Yes']
            if certs:
                print(f"  • Certifications: {', '.join(certs)}")
        
        # Step 6: Apply job-specific formatting
        custom_requirements = processor._convert_job_requirements_to_template(job_requirements)
        
        formatted_notes = extractor.format_for_role(
            all_data=all_data,
            role_type=job_requirements['role_type'],
            custom_requirements=custom_requirements
        )
        
        # Add candidate info to notes
        final_notes = processor._add_candidate_info_to_notes(formatted_notes, all_data['candidate_info'])
        
        # Add processing summary
        final_notes += "\n\nDocument Processing Summary:"
        final_notes += f"\n• Questionnaire analyzed from local files ({len(os.listdir(questionnaire_folder))-1} pages)"
        if attachment_results['processing_log']:
            for log in attachment_results['processing_log']:
                final_notes += f"\n• {log}"
        
        # Step 7: Update CATS
        print("\n📤 Updating CATS with analysis results...")
        success = cats.update_candidate_notes(candidate_id, final_notes)
        
        if success:
            print("✅ Successfully updated candidate notes in CATS!")
        
        # Show final notes
        print("\n" + "=" * 70)
        print("FINAL NOTES:")
        print("=" * 70)
        print(final_notes)
        print("=" * 70)
        
        # Save results
        output_file = f"local_questionnaire_result_{candidate_id}.txt"
        with open(output_file, 'w') as f:
            f.write(f"CANDIDATE PROCESSING WITH LOCAL QUESTIONNAIRE\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"{'=' * 70}\n\n")
            
            f.write(f"Candidate: {candidate_name} (ID: {candidate_id})\n")
            f.write(f"Job: {job_requirements['source']['job_title']} (ID: {job_id})\n\n")
            
            f.write("FINAL NOTES:\n")
            f.write("-" * 30 + "\n")
            f.write(final_notes)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        return {
            'success': success,
            'candidate_name': candidate_name,
            'job_title': job_requirements['source']['job_title'],
            'notes': final_notes,
            'extracted_data': all_data
        }
        
    except Exception as e:
        logger.error(f"Error processing candidate: {e}")
        return {'error': str(e)}

def main():
    # Process Gaétan with local questionnaire
    result = process_with_local_questionnaire(
        candidate_id=399702647,
        job_id=16612581,  # Heavy Equipment Technician
        questionnaire_folder='/home/gotime2022/recruitment_ops/questionnaire_images'
    )
    
    return result

if __name__ == "__main__":
    main()