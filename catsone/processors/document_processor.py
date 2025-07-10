#!/usr/bin/env python3
"""
Multi-Document Processing for Recruitment Analysis
Handles PDF, DOCX, and structured data from CATS
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Document processing libraries
import requests
from docx import Document  # python-docx for DOCX files
import PyPDF2
import fitz  # PyMuPDF for better PDF text extraction
from PIL import Image
import pytesseract  # OCR for PDF checkboxes

# AI processing
import google.generativeai as genai

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process multiple document types for comprehensive candidate analysis"""
    
    def __init__(self):
        self.cats_api_key = os.getenv("CATS_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    async def process_candidate_documents(self, candidate_id: int) -> Dict:
        """Process all available documents for a candidate"""
        
        try:
            # Get candidate data and attachments
            candidate_data = await self.get_candidate_data(candidate_id)
            attachments = candidate_data.get('attachments', [])
            custom_fields = candidate_data.get('custom_fields', [])
            
            # Categorize documents
            documents = await self.categorize_documents(attachments)
            
            # Determine analysis level
            has_interview_notes = documents.get('interview_notes') is not None
            analysis_level = "enhanced" if has_interview_notes else "basic"
            
            # Process each document type
            processed_data = {
                'candidate_id': candidate_id,
                'analysis_level': analysis_level,
                'timestamp': datetime.now().isoformat(),
                'documents_processed': [],
                'resume_analysis': None,
                'questionnaire_analysis': None,
                'interview_analysis': None,
                'custom_fields_analysis': None
            }
            
            # Process Resume
            if documents.get('resume'):
                logger.info(f"Processing resume for candidate {candidate_id}")
                processed_data['resume_analysis'] = await self.process_resume(
                    documents['resume']
                )
                processed_data['documents_processed'].append('resume')
            
            # Process Questionnaire
            if documents.get('questionnaire'):
                logger.info(f"Processing questionnaire for candidate {candidate_id}")
                processed_data['questionnaire_analysis'] = await self.process_questionnaire(
                    documents['questionnaire']
                )
                processed_data['documents_processed'].append('questionnaire')
            
            # Process Interview Notes (if available)
            if documents.get('interview_notes'):
                logger.info(f"Processing interview notes for candidate {candidate_id}")
                processed_data['interview_analysis'] = await self.process_interview_notes(
                    documents['interview_notes']
                )
                processed_data['documents_processed'].append('interview_notes')
            
            # Process Custom Fields
            if custom_fields:
                logger.info(f"Processing custom fields for candidate {candidate_id}")
                processed_data['custom_fields_analysis'] = await self.process_custom_fields(
                    custom_fields
                )
                processed_data['documents_processed'].append('custom_fields')
            
            # Generate comprehensive analysis
            processed_data['comprehensive_analysis'] = await self.generate_comprehensive_analysis(
                processed_data
            )
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing documents for candidate {candidate_id}: {e}")
            return {'error': str(e), 'candidate_id': candidate_id}
    
    async def categorize_documents(self, attachments: List[Dict]) -> Dict:
        """Categorize attachments by document type"""
        
        documents = {
            'resume': None,
            'questionnaire': None,
            'interview_notes': None,
            'other': []
        }
        
        for attachment in attachments:
            filename = attachment.get('filename', '').lower()
            
            # Resume detection
            if (attachment.get('is_resume') or 
                any(word in filename for word in ['resume', 'cv', 'curriculum'])):
                documents['resume'] = attachment
            
            # Interview notes detection
            elif (filename.endswith('.docx') and 
                  any(word in filename for word in ['interview', 'meeting', 'notes', 'call'])):
                documents['interview_notes'] = attachment
            
            # Questionnaire detection  
            elif (filename.endswith('.pdf') and 
                  any(word in filename for word in ['questionnaire', 'form', 'application', 'survey'])):
                documents['questionnaire'] = attachment
            
            else:
                documents['other'].append(attachment)
        
        return documents
    
    async def process_resume(self, resume_attachment: Dict) -> Dict:
        """Extract and analyze resume content"""
        
        try:
            # Download and extract text
            file_content = await self.download_attachment(resume_attachment['id'])
            text_content = await self.extract_pdf_text(file_content)
            
            # AI analysis
            analysis_prompt = f"""
            Analyze this resume for a skilled trades/heavy equipment position:
            
            {text_content}
            
            Extract and structure:
            1. Current position and company
            2. Years of experience (total and by equipment type)  
            3. Equipment brands and types operated
            4. Certifications and licenses
            5. Key achievements and accomplishments
            6. Education and training
            7. Skills and competencies
            8. Red flags or concerns
            
            Return as structured JSON.
            """
            
            if self.model:
                response = self.model.generate_content(analysis_prompt)
                analysis = self.parse_ai_response(response.text)
            else:
                analysis = {'error': 'Gemini API not configured'}
            
            return {
                'filename': resume_attachment.get('filename'),
                'text_content': text_content[:1000] + "..." if len(text_content) > 1000 else text_content,
                'analysis': analysis,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            return {'error': str(e)}
    
    async def process_questionnaire(self, questionnaire_attachment: Dict) -> Dict:
        """Extract questionnaire data including checkboxes via OCR"""
        
        try:
            # Download PDF
            file_content = await self.download_attachment(questionnaire_attachment['id'])
            
            # Extract text content
            text_content = await self.extract_pdf_text(file_content)
            
            # Extract images for OCR (checkbox detection)
            checkbox_data = await self.extract_checkbox_data(file_content)
            
            # AI analysis to structure the questionnaire data
            analysis_prompt = f"""
            Analyze this filled questionnaire for skilled trades recruitment:
            
            Text Content:
            {text_content}
            
            Checkbox/Form Data:
            {checkbox_data}
            
            Extract and structure:
            1. Equipment operated (with years of experience)
            2. Certifications held
            3. Site preferences and availability  
            4. Salary expectations
            5. Training completed
            6. Safety record
            7. Availability and start date
            8. Special skills or endorsements
            9. Any restrictions or limitations
            
            Return as structured JSON with clear categories.
            """
            
            if self.model:
                response = self.model.generate_content(analysis_prompt)
                analysis = self.parse_ai_response(response.text)
            else:
                analysis = {'error': 'Gemini API not configured'}
            
            return {
                'filename': questionnaire_attachment.get('filename'),
                'text_content': text_content,
                'checkbox_data': checkbox_data,
                'analysis': analysis,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing questionnaire: {e}")
            return {'error': str(e)}
    
    async def process_interview_notes(self, interview_attachment: Dict) -> Dict:
        """Process DOCX interview notes"""
        
        try:
            # Download DOCX file
            file_content = await self.download_attachment(interview_attachment['id'])
            
            # Extract text from DOCX
            text_content = await self.extract_docx_text(file_content)
            
            # AI analysis for interview insights
            analysis_prompt = f"""
            Analyze these interview notes for recruitment decision-making:
            
            {text_content}
            
            Extract and analyze:
            1. Candidate's personality and communication style
            2. Technical knowledge demonstrated
            3. Experience details and stories shared
            4. Cultural fit indicators
            5. Motivation and career goals
            6. Any concerns or red flags mentioned
            7. Interviewer's overall impression
            8. Recommended next steps
            9. Salary discussion (if any)
            10. Questions the candidate asked
            
            Provide insights for hiring managers. Return as structured JSON.
            """
            
            if self.model:
                response = self.model.generate_content(analysis_prompt)
                analysis = self.parse_ai_response(response.text)
            else:
                analysis = {'error': 'Gemini API not configured'}
            
            return {
                'filename': interview_attachment.get('filename'),
                'text_content': text_content,
                'analysis': analysis,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing interview notes: {e}")
            return {'error': str(e)}
    
    async def process_custom_fields(self, custom_fields: List[Dict]) -> Dict:
        """Process structured custom field data from CATS"""
        
        try:
            structured_data = {}
            
            for field in custom_fields:
                field_def = field.get('_embedded', {}).get('definition', {})
                field_name = field_def.get('name', 'unknown')
                field_value = field.get('value')
                field_type = field_def.get('field', {}).get('type')
                
                if field_value is not None:
                    if field_type == 'checkboxes' and isinstance(field_value, list):
                        # Multi-select checkboxes
                        selections = field_def.get('field', {}).get('selections', [])
                        selected_labels = []
                        for selection in selections:
                            if selection.get('id') in field_value:
                                selected_labels.append(selection.get('label'))
                        structured_data[field_name] = selected_labels
                    
                    elif field_type == 'dropdown':
                        # Single dropdown
                        selections = field_def.get('field', {}).get('selections', [])
                        for selection in selections:
                            if selection.get('id') == field_value:
                                structured_data[field_name] = selection.get('label')
                                break
                    
                    else:
                        # Text, date, checkbox, etc.
                        structured_data[field_name] = field_value
            
            return {
                'structured_data': structured_data,
                'fields_processed': len([f for f in custom_fields if f.get('value') is not None]),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing custom fields: {e}")
            return {'error': str(e)}
    
    async def generate_comprehensive_analysis(self, processed_data: Dict) -> Dict:
        """Generate final comprehensive analysis combining all documents"""
        
        try:
            analysis_level = processed_data.get('analysis_level', 'basic')
            
            # Compile all data
            all_data = {
                'resume': processed_data.get('resume_analysis'),
                'questionnaire': processed_data.get('questionnaire_analysis'), 
                'custom_fields': processed_data.get('custom_fields_analysis'),
                'interview': processed_data.get('interview_analysis') if analysis_level == 'enhanced' else None
            }
            
            # Create comprehensive prompt
            comprehensive_prompt = f"""
            Create a comprehensive candidate analysis for hiring managers based on:
            
            Analysis Level: {analysis_level.upper()}
            
            Resume Analysis:
            {all_data.get('resume', 'Not available')}
            
            Questionnaire Analysis:
            {all_data.get('questionnaire', 'Not available')}
            
            Custom Fields Data:
            {all_data.get('custom_fields', 'Not available')}
            
            {"Interview Analysis:" if analysis_level == 'enhanced' else ""}
            {all_data.get('interview', '') if analysis_level == 'enhanced' else ''}
            
            Provide:
            1. Executive Summary (2-3 sentences)
            2. Overall Match Score (0-100%)
            3. Key Strengths (top 5)
            4. Potential Concerns (if any)
            5. Equipment Expertise Summary
            6. Certification Status
            7. Recommended Action (hire/interview/pass)
            8. Salary Range Recommendation
            {"9. Interview Insights (personality, fit, concerns)" if analysis_level == 'enhanced' else ""}
            
            Return as structured JSON for Slack notification formatting.
            """
            
            if self.model:
                response = self.model.generate_content(comprehensive_prompt)
                analysis = self.parse_ai_response(response.text)
            else:
                analysis = {'error': 'Gemini API not configured'}
            
            return {
                'analysis_level': analysis_level,
                'overall_analysis': analysis,
                'documents_included': processed_data.get('documents_processed', []),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {e}")
            return {'error': str(e)}
    
    # Helper methods
    async def get_candidate_data(self, candidate_id: int) -> Dict:
        """Get full candidate data from CATS API"""
        url = f"https://api.catsone.com/v3/candidates/{candidate_id}"
        headers = {
            "Authorization": f"Token {self.cats_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'attachments': data.get('_embedded', {}).get('attachments', []),
                'custom_fields': data.get('_embedded', {}).get('custom_fields', []),
                'candidate_info': data
            }
        else:
            raise Exception(f"Failed to get candidate data: {response.status_code}")
    
    async def download_attachment(self, attachment_id: int) -> bytes:
        """Download attachment from CATS"""
        url = f"https://api.catsone.com/v3/attachments/{attachment_id}/download"
        headers = {"Authorization": f"Token {self.cats_api_key}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to download attachment: {response.status_code}")
    
    async def extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF using PyMuPDF"""
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    async def extract_docx_text(self, docx_content: bytes) -> str:
        """Extract text from DOCX file"""
        # Save temporarily to process with python-docx
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp.write(docx_content)
            tmp.flush()
            
            doc = Document(tmp.name)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            os.unlink(tmp.name)
            return text
    
    async def extract_checkbox_data(self, pdf_content: bytes) -> str:
        """Extract checkbox data using OCR (basic implementation)"""
        # This would need more sophisticated OCR for checkbox detection
        # For now, return placeholder
        return "Checkbox extraction not yet implemented - would use OCR analysis"
    
    def parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response, handling both JSON and text responses"""
        try:
            import json
            # Try to parse as JSON
            return json.loads(response_text)
        except:
            # If not JSON, return as text
            return {'ai_response': response_text}


# Example usage
if __name__ == "__main__":
    processor = DocumentProcessor()
    # result = await processor.process_candidate_documents(407373086)