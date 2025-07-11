#!/usr/bin/env python3
"""
Intelligent Candidate Processor - Extracts everything, filters by job requirements
"""

import os
import sys
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
from catsone.processors.dynamic_extraction_system import DynamicExtractionSystem
from catsone.processors.job_requirements_extractor import JobRequirementsExtractor
from catsone.processors.comprehensive_attachment_processor import ComprehensiveAttachmentProcessor
from catsone.processors.ai_notes_formatter import AINotesFormatter

logger = logging.getLogger(__name__)

class IntelligentCandidateProcessor:
    """Process candidates based on job-specific requirements"""
    
    def __init__(self):
        self.cats = CATSClient()
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.vision_analyzer = VisionQuestionnaireAnalyzer(self.gemini_key)
        self.extractor = DynamicExtractionSystem()
        self.job_extractor = JobRequirementsExtractor()
        self.attachment_processor = ComprehensiveAttachmentProcessor()
        self.ai_formatter = AINotesFormatter()
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    def process_candidate_for_job(self, candidate_id: int, job_id: int) -> Dict[str, Any]:
        """Process candidate with job-specific filtering"""
        
        try:
            # Step 1: Get job requirements
            logger.info(f"Getting job requirements for job {job_id}")
            job_data = self.cats.get_job_details(job_id)
            if not job_data:
                return {'error': 'Job not found'}
            
            job_requirements = self.job_extractor.extract_job_requirements(job_data)
            logger.info(f"Extracted requirements for: {job_requirements['source']['job_title']}")
            
            # Step 2: Get candidate info
            candidate = self.cats.get_candidate_details(candidate_id)
            if not candidate:
                return {'error': 'Candidate not found'}
            
            candidate_name = f"{candidate.get('first_name')} {candidate.get('last_name')}"
            
            # Step 3: Process all attachments
            logger.info(f"Processing all attachments for candidate {candidate_id}")
            attachment_results = self.attachment_processor.process_all_attachments(candidate_id)
            
            if 'error' in attachment_results:
                return {'error': f"Attachment processing failed: {attachment_results['error']}"}
            
            logger.info(f"Found {attachment_results['attachments_found']} attachments")
            
            # Initialize data structure
            all_data = {
                'candidate_info': {
                    'name': candidate_name,
                    'location': f"{candidate.get('city', '')}, {candidate.get('state', '')}".strip(', '),
                    'candidate_id': candidate_id
                },
                'responses': {},
                'equipment': {
                    'brands_available': [], 
                    'brands_selected': [],
                    'brands_worked_with': [],
                    'equipment_types': []
                },
                'certifications': {},
                'resume_data': attachment_results.get('resume_data'),
                'interview_notes': attachment_results.get('interview_notes')
            }
            
            # Step 4: Process questionnaire if found
            if attachment_results.get('questionnaire_data'):
                logger.info("Analyzing questionnaire data...")
                questionnaire_data = attachment_results['questionnaire_data']
                
                # Ensure questionnaire_data is a dict
                if not isinstance(questionnaire_data, dict):
                    logger.error(f"Questionnaire data is not a dict: {type(questionnaire_data)}")
                    questionnaire_data = {}
                
                # Check for Claude vision format (candidate_profile with all_responses)
                if questionnaire_data and 'candidate_profile' in questionnaire_data:
                    logger.info("Processing Claude vision questionnaire data")
                    profile = questionnaire_data['candidate_profile']
                    
                    # Ensure profile is a dict
                    if not isinstance(profile, dict):
                        logger.error(f"Profile is not a dict: {type(profile)}, value: {profile}")
                        profile = {}
                    
                    # Extract equipment from all_responses
                    for response in profile.get('all_responses', []):
                        if response.get('equipment_specific', {}).get('is_equipment_question'):
                            # Add selected equipment
                            for selection in response.get('actual_selections', []):
                                if 'CAT' in selection or 'Hitachi' in selection or 'Komatsu' in selection:
                                    all_data['equipment']['brands_selected'].append(selection)
                        
                        # Check for certifications
                        if 'qualitative fit test' in response.get('question_text', '').lower():
                            if response.get('actual_selections') == ['Yes']:
                                all_data['certifications']['qualitative_fit_test'] = 'Yes'
                    
                    # Get equipment from candidate_profile
                    if 'equipment_experience' in profile:
                        equipment = profile['equipment_experience']
                        all_data['equipment']['brands_worked_with'].extend(equipment.get('brands_worked_with', []))
                        all_data['equipment']['equipment_types'].extend(equipment.get('equipment_types', []))
                
                # Old format compatibility
                elif questionnaire_data and 'responses' in questionnaire_data:
                    # Extract ALL data from questionnaire
                    questionnaire_extracted = self.extractor.extract_all_questionnaire_data(questionnaire_data)
                    
                    # Merge questionnaire data
                    all_data['responses'].update(questionnaire_extracted.get('responses', {}))
                    all_data['equipment'] = questionnaire_extracted.get('equipment', all_data['equipment'])
                    all_data['certifications'].update(questionnaire_extracted.get('certifications', {}))
            
            # Step 5: Apply job-specific formatting
            # Use AI formatter if we have questionnaire data
            if attachment_results.get('questionnaire_data') and isinstance(attachment_results['questionnaire_data'], dict):
                logger.info("Using AI formatter for comprehensive notes")
                formatted_notes = self.ai_formatter.format_questionnaire_notes(
                    questionnaire_data=attachment_results['questionnaire_data'],
                    job_requirements=job_requirements
                )
            else:
                # Fallback to template-based formatting
                logger.info("Using template-based formatter")
                custom_requirements = self._convert_job_requirements_to_template(job_requirements)
                formatted_notes = self.extractor.format_for_role(
                    all_data=all_data,
                    role_type=job_requirements['role_type'],
                    custom_requirements=custom_requirements
                )
            
            # Add candidate info to notes
            final_notes = self._add_candidate_info_to_notes(formatted_notes, all_data['candidate_info'])
            
            # Don't add attachment processing log to notes - it's just debug info
            
            # Step 6: Update CATS
            success = self.cats.update_candidate_notes(candidate_id, final_notes)
            
            # Step 7: Send Slack notification if notes were successfully updated
            if success:
                self._send_slack_notification(
                    candidate_id=candidate_id,
                    candidate_name=candidate_name,
                    job_title=job_requirements['source']['job_title'],
                    job_id=job_id
                )
            
            return {
                'success': success,
                'candidate_name': candidate_name,
                'job_title': job_requirements['source']['job_title'],
                'notes': final_notes,
                'job_requirements': job_requirements,
                'extracted_data': all_data,
                'attachment_results': attachment_results
            }
            
        except Exception as e:
            logger.error(f"Error processing candidate: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'error': str(e)}
    
    def _convert_job_requirements_to_template(self, job_requirements: Dict) -> Dict:
        """Convert job requirements to template format"""
        
        template = {
            'required_certs': job_requirements['required_certifications'],
            'exclude_certs': [],  # Will be populated based on job notes
            'important_brands': job_requirements['required_brands'] + job_requirements['preferred_brands'],
            'important_equipment': job_requirements['required_equipment'] + job_requirements['preferred_equipment'],
            'exclude_info': job_requirements['exclude_from_notes'],
            'highlight_info': job_requirements['highlight_in_notes'],
            'custom_filters': job_requirements['custom_filters']
        }
        
        # Add standard exclusions if not specified
        if not template['exclude_info']:
            template['exclude_info'] = ['drug test', 'housing', 'cooking', 'rotational shifts']
        
        return template
    
    def _add_candidate_info_to_notes(self, notes: str, candidate_info: Dict) -> str:
        """Add candidate info to formatted notes"""
        
        # For the new email format, replace placeholder text with actual name
        if candidate_info.get('name'):
            # Replace "Here's a strong candidate" with name if available
            notes = notes.replace(
                "Here's a strong candidate for the Heavy Equipment Technician position:",
                f"Here's a strong candidate for the Heavy Equipment Technician position - {candidate_info['name']}:"
            )
        
        return notes
    
    def _send_slack_notification(self, candidate_id: int, candidate_name: str, job_title: str, job_id: int):
        """Send Slack notification when AI notes are generated"""
        
        if not self.slack_webhook_url or self.slack_webhook_url == "your_slack_webhook_here":
            logger.info("Slack webhook not configured, skipping notification")
            return
        
        try:
            # Build CATS URL for direct link
            cats_url = f"https://bigcountryequipmentrepair.catsone.com/index.php?m=candidates&a=show&candidateID={candidate_id}"
            
            # Create Slack message
            slack_message = {
                "text": f"🤖 AI Notes Generated for {candidate_name}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🤖 AI Notes Generated",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Candidate:*\n{candidate_name}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*ID:*\n{candidate_id}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Position:*\n{job_title}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Job ID:*\n{job_id}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"<@ryan.angel> AI notes have been generated. Please review the candidate's profile."
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View in CATS",
                                    "emoji": True
                                },
                                "url": cats_url,
                                "style": "primary"
                            }
                        ]
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(self.slack_webhook_url, json=slack_message)
            
            if response.status_code == 200:
                logger.info(f"Slack notification sent for candidate {candidate_id}")
            else:
                logger.error(f"Failed to send Slack notification: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            # Don't fail the whole process if Slack notification fails


def process_candidate(candidate_id: int, job_id: int):
    """Main function to process a candidate"""
    
    processor = IntelligentCandidateProcessor()
    result = processor.process_candidate_for_job(candidate_id, job_id)
    
    if result.get('success'):
        print(f"✅ Successfully processed {result['candidate_name']} for {result['job_title']}")
        print("\nNotes updated in CATS:")
        print("-" * 60)
        print(result['notes'])
        
        # Show attachment processing summary
        if result.get('attachment_results'):
            print("\nAttachments processed:")
            print("-" * 60)
            for log_entry in result['attachment_results']['processing_log']:
                print(f"  {log_entry}")
    else:
        print(f"❌ Processing failed: {result.get('error')}")
    
    return result


if __name__ == "__main__":
    # Test with Gaétan for Heavy Equipment Technician job
    process_candidate(
        candidate_id=399702647,
        job_id=16612581  # Heavy Equipment Technician job
    )