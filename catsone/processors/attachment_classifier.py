#!/usr/bin/env python3
"""
Attachment Classifier - Identifies and processes different attachment types
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class AttachmentClassifier:
    """Classify and process different types of candidate attachments"""
    
    def __init__(self):
        # Patterns to identify attachment types
        self.patterns = {
            'resume': {
                'filename_patterns': [
                    r'resume', r'cv', r'curriculum', r'vitae', 
                    r'work.?history', r'experience'
                ],
                'content_patterns': [
                    r'work experience', r'employment history', 
                    r'education', r'skills', r'references'
                ],
                'common_extensions': ['.pdf', '.doc', '.docx'],
                'priority': 1
            },
            'questionnaire': {
                'filename_patterns': [
                    r'questionnaire', r'form', r'application', 
                    r'survey', r'assessment', r'questions',
                    r'recruiting\s*-\s*dayforce',  # Matches "Recruiting - Dayforce" with any spacing
                    r'dayforce',  # Match any filename with "dayforce"
                    r'inbox.*dayforce'  # Match "Inbox - Message Center - Dayforce" pattern
                ],
                'content_patterns': [
                    r'do you have', r'are you comfortable', 
                    r'yes\s*no', r'check all that apply',
                    r'please select', r'which of the following'
                ],
                'common_extensions': ['.pdf', '.png', '.jpg'],
                'priority': 2
            },
            'interview_notes': {
                'filename_patterns': [
                    r'interview', r'notes', r'meeting', 
                    r'discussion', r'conversation', r'google.?meet',
                    r'teams', r'zoom', r'call.?notes'
                ],
                'content_patterns': [
                    r'discussed', r'mentioned', r'asked about',
                    r'candidate said', r'follow.?up', r'next steps'
                ],
                'common_extensions': ['.pdf', '.doc', '.docx', '.txt'],
                'priority': 3
            },
            'reference': {
                'filename_patterns': [
                    r'reference', r'recommendation', r'letter'
                ],
                'content_patterns': [
                    r'recommend', r'worked with', r'behalf of'
                ],
                'common_extensions': ['.pdf', '.doc', '.docx'],
                'priority': 4
            },
            'certification': {
                'filename_patterns': [
                    r'certificate', r'certification', r'license',
                    r'red.?seal', r'journeyman', r'ticket'
                ],
                'content_patterns': [
                    r'certif', r'hereby', r'awarded', r'completion'
                ],
                'common_extensions': ['.pdf', '.jpg', '.png'],
                'priority': 5
            }
        }
    
    def classify_attachments(self, attachments: List[Dict]) -> Dict[str, List[Dict]]:
        """Classify attachments by type"""
        
        classified = {
            'resume': [],
            'questionnaire': [],
            'interview_notes': [],
            'reference': [],
            'certification': [],
            'unknown': []
        }
        
        for attachment in attachments:
            attachment_type = self._identify_attachment_type(attachment)
            
            if attachment_type in classified:
                classified[attachment_type].append(attachment)
            else:
                classified['unknown'].append(attachment)
        
        # Log classification results
        logger.info("Attachment classification results:")
        for atype, items in classified.items():
            if items:
                logger.info(f"  {atype}: {len(items)} files")
                for item in items:
                    logger.info(f"    - {item.get('filename')}")
        
        return classified
    
    def _identify_attachment_type(self, attachment: Dict) -> str:
        """Identify the type of an attachment"""
        
        filename = attachment.get('filename', '').lower()
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Check if CATS marked it as resume
        if attachment.get('is_resume'):
            return 'resume'
        
        # Score each type based on filename
        scores = {}
        
        for atype, patterns in self.patterns.items():
            score = 0
            
            # Check filename patterns
            for pattern in patterns['filename_patterns']:
                if re.search(pattern, filename):
                    score += 10
            
            # Check extension
            if file_ext in patterns['common_extensions']:
                score += 5
            
            # Check metadata hints
            if attachment.get('description'):
                desc_lower = attachment['description'].lower()
                for pattern in patterns['filename_patterns']:
                    if re.search(pattern, desc_lower):
                        score += 8
            
            scores[atype] = score
        
        # Find highest scoring type
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                return best_type
        
        # Additional heuristics
        if 'page' in filename and file_ext in ['.png', '.jpg', '.pdf']:
            # Multi-page document, likely questionnaire
            return 'questionnaire'
        
        return 'unknown'
    
    def process_classified_attachments(self, classified: Dict[str, List[Dict]], 
                                     candidate_id: int) -> Dict[str, Any]:
        """Process each type of attachment appropriately"""
        
        results = {
            'resume_data': None,
            'questionnaire_data': None,
            'interview_insights': None,
            'additional_info': {},
            'processing_log': []
        }
        
        # Process resume
        if classified['resume']:
            # Take the most recent resume
            resume = sorted(classified['resume'], 
                          key=lambda x: x.get('created_at', ''), 
                          reverse=True)[0]
            results['resume_data'] = {
                'attachment_id': resume['id'],
                'filename': resume['filename'],
                'needs_extraction': True
            }
            results['processing_log'].append(f"Found resume: {resume['filename']}")
        
        # Process questionnaires
        if classified['questionnaire']:
            # May have multiple pages
            questionnaires = classified['questionnaire']
            
            # Check if they're numbered pages
            numbered_pages = []
            other_questionnaires = []
            
            for q in questionnaires:
                if re.search(r'page.?\d+', q['filename'].lower()):
                    numbered_pages.append(q)
                else:
                    other_questionnaires.append(q)
            
            if numbered_pages:
                # Sort by page number
                numbered_pages.sort(key=lambda x: self._extract_page_number(x['filename']))
                results['questionnaire_data'] = {
                    'type': 'multi_page',
                    'pages': numbered_pages,
                    'needs_vision_analysis': True
                }
                results['processing_log'].append(f"Found multi-page questionnaire: {len(numbered_pages)} pages")
            elif other_questionnaires:
                results['questionnaire_data'] = {
                    'type': 'single',
                    'attachments': other_questionnaires,
                    'needs_vision_analysis': True
                }
                results['processing_log'].append(f"Found questionnaire(s): {len(other_questionnaires)} files")
        
        # Process interview notes
        if classified['interview_notes']:
            # Usually just one, but could have multiple interviews
            interview_docs = classified['interview_notes']
            results['interview_insights'] = {
                'documents': interview_docs,
                'needs_text_extraction': True,
                'extraction_prompt': self._get_interview_extraction_prompt()
            }
            results['processing_log'].append(f"Found interview notes: {len(interview_docs)} documents")
        
        # Process certifications
        if classified['certification']:
            results['additional_info']['certifications'] = classified['certification']
            results['processing_log'].append(f"Found certifications: {len(classified['certification'])} files")
        
        # Process references
        if classified['reference']:
            results['additional_info']['references'] = classified['reference']
            results['processing_log'].append(f"Found references: {len(classified['reference'])} files")
        
        return results
    
    def _extract_page_number(self, filename: str) -> int:
        """Extract page number from filename"""
        
        match = re.search(r'page.?(\d+)', filename.lower())
        if match:
            return int(match.group(1))
        return 999  # Put non-numbered at end
    
    def _get_interview_extraction_prompt(self) -> str:
        """Get prompt for extracting interview insights"""
        
        return """
        Extract key information from these interview notes:
        
        1. Technical Skills Discussed:
           - Equipment experience mentioned
           - Specific brands or models
           - Problem-solving examples
           
        2. Work Experience Details:
           - Specific projects or achievements
           - Leadership experience
           - Challenges overcome
           
        3. Soft Skills Observed:
           - Communication ability
           - Team collaboration
           - Work ethic indicators
           
        4. Red Flags or Concerns:
           - Any hesitations
           - Knowledge gaps identified
           - Availability issues
           
        5. Follow-up Items:
           - Additional information needed
           - References to check
           - Next steps discussed
           
        6. Overall Impression:
           - Interviewer's assessment
           - Culture fit
           - Technical competency
           
        Focus on concrete details and specific examples mentioned.
        """


def create_attachment_summary(classified: Dict[str, List[Dict]], 
                            processed: Dict[str, Any]) -> str:
    """Create summary of attachments for notes"""
    
    summary_lines = []
    
    summary_lines.append("DOCUMENT ANALYSIS SUMMARY:")
    summary_lines.append("-" * 25)
    
    # Resume
    if processed.get('resume_data'):
        summary_lines.append(f"• Resume: {processed['resume_data']['filename']}")
    
    # Questionnaire
    if processed.get('questionnaire_data'):
        qdata = processed['questionnaire_data']
        if qdata['type'] == 'multi_page':
            summary_lines.append(f"• Questionnaire: {len(qdata['pages'])} pages analyzed")
        else:
            summary_lines.append(f"• Questionnaire: {len(qdata['attachments'])} documents")
    
    # Interview notes
    if processed.get('interview_insights'):
        docs = processed['interview_insights']['documents']
        summary_lines.append(f"• Interview Notes: {len(docs)} sessions")
        for doc in docs:
            summary_lines.append(f"  - {doc['filename']}")
    
    # Other attachments
    if processed.get('additional_info'):
        for atype, items in processed['additional_info'].items():
            if items:
                summary_lines.append(f"• {atype.title()}: {len(items)} files")
    
    return '\n'.join(summary_lines)