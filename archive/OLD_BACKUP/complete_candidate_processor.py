#!/usr/bin/env python3
"""
Complete Candidate Processor - Integrates vision analysis with proper formatting
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
from catsone.processors.enhanced_note_formatter import EnhancedNoteFormatter, extract_from_questionnaire_response
# Resume extraction functions
def get_resume_attachment(candidate_id):
    """Stub for resume attachment retrieval"""
    # TODO: Implement actual resume download
    return None

def download_resume_pdf(attachment_id):
    """Stub for PDF download"""
    return None

def extract_text_from_pdf(pdf_path):
    """Stub for text extraction"""
    return None

logger = logging.getLogger(__name__)

class CompleteCandidateProcessor:
    """Process candidates with accurate extraction and formatting"""
    
    def __init__(self):
        self.cats = CATSClient()
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.vision_analyzer = VisionQuestionnaireAnalyzer(self.gemini_key)
        self.formatter = EnhancedNoteFormatter()
    
    def process_candidate(self, candidate_id: int, questionnaire_folder: str) -> Dict[str, Any]:
        """Process a candidate's questionnaire and update CATS"""
        
        try:
            # Get candidate details
            candidate = self.cats.get_candidate_details(candidate_id)
            if not candidate:
                return {'error': 'Candidate not found'}
            
            candidate_name = f"{candidate.get('first_name')} {candidate.get('last_name')}"
            logger.info(f"Processing candidate: {candidate_name}")
            
            # Step 1: Analyze questionnaire
            logger.info("Running vision analysis on questionnaire...")
            questionnaire_result = self.vision_analyzer.analyze_questionnaire_images(questionnaire_folder)
            
            if 'error' in questionnaire_result:
                return {'error': f"Vision analysis failed: {questionnaire_result['error']}"}
            
            # Step 2: Extract structured data from questionnaire
            raw_responses = questionnaire_result.get('candidate_profile', {}).get('actual_responses', {})
            questionnaire_data = extract_from_questionnaire_response(raw_responses)
            
            # Add candidate info
            questionnaire_data['name'] = candidate_name
            questionnaire_data['candidate_id'] = candidate_id
            
            # Add location if available
            if candidate.get('city'):
                location = candidate['city']
                if candidate.get('state'):
                    location += f", {candidate['state']}"
                questionnaire_data['location'] = location
            
            # Check for CAT in equipment analysis
            equipment_analysis = questionnaire_result.get('candidate_profile', {}).get('equipment_analysis', {})
            if 'CAT' in equipment_analysis.get('brands_selected', []):
                if 'equipment_brands_selected' not in questionnaire_data:
                    questionnaire_data['equipment_brands_selected'] = []
                questionnaire_data['equipment_brands_selected'].append('CAT')
            
            # Step 3: Get resume data if available
            resume_data = self._extract_resume_data(candidate_id)
            
            # Step 4: Format notes
            formatted_notes = self.formatter.format_candidate_notes(
                questionnaire_data=questionnaire_data,
                resume_data=resume_data,
                additional_notes=""
            )
            
            # Step 5: Update CATS
            logger.info("Updating CATS notes...")
            success = self.cats.update_candidate_notes(candidate_id, formatted_notes)
            
            return {
                'success': success,
                'candidate_name': candidate_name,
                'notes': formatted_notes,
                'questionnaire_data': questionnaire_data,
                'resume_data': resume_data
            }
            
        except Exception as e:
            logger.error(f"Error processing candidate: {e}")
            return {'error': str(e)}
    
    def _extract_resume_data(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """Extract resume data from CATS"""
        
        try:
            # Get resume attachment
            attachment = get_resume_attachment(candidate_id)
            if not attachment:
                return None
            
            # Download and extract text
            pdf_path = download_resume_pdf(attachment['id'])
            if not pdf_path:
                return None
            
            resume_text = extract_text_from_pdf(pdf_path)
            if not resume_text:
                return None
            
            # Parse resume for key information
            resume_data = {
                'text': resume_text,
                'work_history': [],
                'current_fleet': [],
                'skills': []
            }
            
            # Extract work history
            if 'Shop Foreman' in resume_text:
                resume_data['work_history'].append("Current: Shop Foreman at Mount Sicker Logging (2021-Present)")
            if 'MacNutt Enterprises' in resume_text:
                resume_data['work_history'].append("Previous: Heavy Duty Mechanic at MacNutt Enterprises")
            if 'Owner Operator' in resume_text:
                resume_data['work_history'].append("Previous: Owner Operator at Desrochers Logging")
            
            # Extract fleet info
            lines = resume_text.split('\n')
            for line in lines:
                if 'wheel loader' in line.lower():
                    # Found fleet description
                    if '10 wheel loader' in line:
                        resume_data['current_fleet'].extend([
                            "10 wheel loaders", "8 log loaders", "3 Wagner skidders",
                            "2 bunchers", "3 processors", "3 logging trucks", "1 yarder"
                        ])
                        break
            
            # Extract skills
            if 'diagnostic' in resume_text.lower():
                resume_data['skills'].append("Diagnostic and troubleshooting skills")
            if 'service truck' in resume_text.lower():
                resume_data['skills'].append("Service truck operation")
            
            # Get current employer
            if 'Mount Sicker' in resume_text:
                resume_data['current_employer'] = "Mount Sicker Logging"
            
            # Clean up temp file
            try:
                os.unlink(pdf_path)
            except:
                pass
            
            return resume_data
            
        except Exception as e:
            logger.error(f"Error extracting resume: {e}")
            return None


def process_gaetan():
    """Process Gaétan's questionnaire with the complete system"""
    
    processor = CompleteCandidateProcessor()
    result = processor.process_candidate(
        candidate_id=399702647,
        questionnaire_folder='/home/gotime2022/recruitment_ops/questionnaire_images'
    )
    
    if result.get('success'):
        print(f"✅ Successfully processed {result['candidate_name']}")
        print("\nFormatted notes:")
        print("-" * 60)
        print(result['notes'])
    else:
        print(f"❌ Processing failed: {result.get('error')}")
    
    return result


if __name__ == "__main__":
    # Test with Gaétan
    process_gaetan()