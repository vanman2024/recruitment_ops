#!/usr/bin/env python3
"""
Comprehensive Attachment Processor - Handles all attachment types
"""

import os
import sys
import logging
import requests
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
from catsone.processors.attachment_classifier import AttachmentClassifier
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
from catsone.processors.dayforce_questionnaire_handler import DayforceQuestionnaireHandler
from catsone.processors.claude_vision_analyzer import ClaudeVisionAnalyzer
import google.generativeai as genai

logger = logging.getLogger(__name__)

class ComprehensiveAttachmentProcessor:
    """Process all types of candidate attachments"""
    
    def __init__(self):
        # Force load environment variables
        from pathlib import Path
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path, override=True)
            
        self.cats = CATSClient()
        self.classifier = AttachmentClassifier()
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Use Claude 4 Opus if available, otherwise fall back to Gemini
        self.claude_key = os.getenv('ANTHROPIC_API_KEY')
        if self.claude_key and self.claude_key != 'your-api-key-here':
            logger.info(f"Using Claude 4 Opus for vision analysis (key: {self.claude_key[:20]}...)")
            self.vision_analyzer = ClaudeVisionAnalyzer(self.claude_key)
        else:
            logger.warning(f"Claude key not found or invalid: {self.claude_key}")
            logger.info("Using Gemini for vision analysis")
            self.vision_analyzer = VisionQuestionnaireAnalyzer(self.gemini_key)
            
        self.dayforce_handler = DayforceQuestionnaireHandler()
    
    def process_all_attachments(self, candidate_id: int) -> Dict[str, Any]:
        """Process all attachments for a candidate"""
        
        results = {
            'candidate_id': candidate_id,
            'attachments_found': 0,
            'resume_data': None,
            'questionnaire_data': None,
            'interview_notes': None,
            'additional_docs': {},
            'processing_log': []
        }
        
        try:
            # Get all attachments
            attachments = self._get_all_attachments(candidate_id)
            results['attachments_found'] = len(attachments)
            
            if not attachments:
                results['processing_log'].append("No attachments found")
                return results
            
            # Classify attachments
            classified = self.classifier.classify_attachments(attachments)
            processed = self.classifier.process_classified_attachments(classified, candidate_id)
            
            # Process each type
            if processed.get('resume_data'):
                results['resume_data'] = self._process_resume(processed['resume_data'])
            
            if processed.get('questionnaire_data'):
                results['questionnaire_data'] = self._process_questionnaire(processed['questionnaire_data'])
            
            if processed.get('interview_insights'):
                results['interview_notes'] = self._process_interview_notes(processed['interview_insights'])
            
            # Add processing log
            results['processing_log'].extend(processed.get('processing_log', []))
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing attachments: {e}")
            results['error'] = str(e)
            return results
    
    def _get_all_attachments(self, candidate_id: int) -> List[Dict]:
        """Get all attachments for a candidate"""
        
        try:
            url = f"{self.cats.base_url}/candidates/{candidate_id}/attachments"
            response = requests.get(url, headers=self.cats.headers)
            
            if response.status_code == 200:
                data = response.json()
                attachments = data.get('_embedded', {}).get('attachments', [])
                logger.info(f"Found {len(attachments)} attachments for candidate {candidate_id}")
                return attachments
            else:
                logger.error(f"Error getting attachments: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching attachments: {e}")
            return []
    
    def _process_resume(self, resume_info: Dict) -> Dict[str, Any]:
        """Process resume attachment"""
        
        try:
            # Download resume
            pdf_path = self._download_attachment(resume_info['attachment_id'])
            if not pdf_path:
                return {'error': 'Could not download resume'}
            
            # Extract text
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()
            
            doc.close()
            
            # Clean up
            os.unlink(pdf_path)
            
            # Extract key information
            resume_data = {
                'text': text,
                'filename': resume_info['filename'],
                'work_history': self._extract_work_history(text),
                'skills': self._extract_skills(text),
                'certifications': self._extract_certifications(text),
                'equipment': self._extract_equipment(text)
            }
            
            return resume_data
            
        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            return {'error': str(e)}
    
    def _process_questionnaire(self, questionnaire_info: Dict) -> Dict[str, Any]:
        """Process questionnaire attachment(s)"""
        
        try:
            if questionnaire_info['type'] == 'multi_page':
                # Download all pages and save to temp folder
                temp_folder = tempfile.mkdtemp()
                
                for i, page_info in enumerate(questionnaire_info['pages']):
                    file_path = self._download_attachment(page_info['id'])
                    if file_path:
                        # Move to temp folder with proper naming
                        new_path = os.path.join(temp_folder, f"page_{i+1}.png")
                        os.rename(file_path, new_path)
                
                # Run vision analysis
                vision_result = self.vision_analyzer.analyze_questionnaire_images(temp_folder)
                
                # Check if this is a Dayforce questionnaire
                is_dayforce = False
                for attachment in questionnaire_info.get('attachments', []):
                    filename = attachment.get('filename', '').lower()
                    # Match "recruiting - dayforce" pattern (ignoring numbers, brackets, etc.)
                    if 'recruiting' in filename and 'dayforce' in filename:
                        is_dayforce = True
                        break
                
                # Apply Dayforce handler if needed
                if is_dayforce:
                    vision_result = self.dayforce_handler.process_dayforce_questionnaire(vision_result)
                
                # Clean up
                import shutil
                shutil.rmtree(temp_folder)
                
                return vision_result
                
            else:
                # Single questionnaire file
                temp_folder = tempfile.mkdtemp()
                
                # Process single file or PDF
                for attachment in questionnaire_info.get('attachments', []):
                    file_path = self._download_attachment(attachment['id'])
                    if file_path:
                        # Check if PDF and convert to images
                        if file_path.endswith('.pdf'):
                            self._convert_pdf_to_images(file_path, temp_folder)
                        else:
                            # Move image to temp folder
                            import shutil
                            shutil.move(file_path, os.path.join(temp_folder, 'page_1.png'))
                
                # Run vision analysis
                vision_result = self.vision_analyzer.analyze_questionnaire_images(temp_folder)
                
                # Check if this is a Dayforce questionnaire
                is_dayforce = False
                for attachment in questionnaire_info.get('attachments', []):
                    filename = attachment.get('filename', '').lower()
                    # Match "recruiting - dayforce" pattern (ignoring numbers, brackets, etc.)
                    if 'recruiting' in filename and 'dayforce' in filename:
                        is_dayforce = True
                        break
                
                # Apply Dayforce handler if needed
                if is_dayforce:
                    vision_result = self.dayforce_handler.process_dayforce_questionnaire(vision_result)
                
                # Clean up
                import shutil
                shutil.rmtree(temp_folder)
                
                return vision_result
                
        except Exception as e:
            logger.error(f"Error processing questionnaire: {e}")
            return {'error': str(e)}
    
    def _process_interview_notes(self, interview_info: Dict) -> Dict[str, Any]:
        """Process interview notes using AI extraction"""
        
        interview_results = {
            'sessions': [],
            'key_insights': {},
            'combined_summary': ""
        }
        
        try:
            for doc in interview_info['documents']:
                # Download document
                file_path = self._download_attachment(doc['id'])
                if not file_path:
                    continue
                
                # Extract text based on file type
                text = ""
                if file_path.endswith('.pdf'):
                    import fitz
                    pdf_doc = fitz.open(file_path)
                    for page in pdf_doc:
                        text += page.get_text()
                    pdf_doc.close()
                else:
                    # Try as text file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                    except:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            text = f.read()
                
                # Clean up
                os.unlink(file_path)
                
                # Extract insights using AI
                insights = self._extract_interview_insights(text, doc['filename'])
                
                interview_results['sessions'].append({
                    'filename': doc['filename'],
                    'insights': insights
                })
            
            # Combine all insights
            if interview_results['sessions']:
                interview_results['combined_summary'] = self._combine_interview_insights(
                    interview_results['sessions']
                )
            
            return interview_results
            
        except Exception as e:
            logger.error(f"Error processing interview notes: {e}")
            return {'error': str(e)}
    
    def _download_attachment(self, attachment_id: int) -> Optional[str]:
        """Download attachment to temp file"""
        
        try:
            url = f"{self.cats.base_url}/attachments/{attachment_id}/download"
            response = requests.get(url, headers=self.cats.headers)
            
            if response.status_code == 200:
                # Save to temp file
                suffix = '.pdf'  # Default
                if 'content-disposition' in response.headers:
                    filename = response.headers['content-disposition']
                    if '.png' in filename:
                        suffix = '.png'
                    elif '.jpg' in filename or '.jpeg' in filename:
                        suffix = '.jpg'
                    elif '.doc' in filename:
                        suffix = '.doc'
                    elif '.txt' in filename:
                        suffix = '.txt'
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(response.content)
                    return temp_file.name
            else:
                logger.error(f"Download failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading attachment: {e}")
            return None
    
    def _extract_interview_insights(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract insights from interview notes using AI"""
        
        prompt = f"""
        Analyze these interview notes and extract key information:
        
        Document: {filename}
        
        {text}
        
        Extract:
        1. Technical skills discussed (equipment, brands, specific experience)
        2. Soft skills observed (communication, teamwork, attitude)
        3. Concerns or red flags mentioned
        4. Positive highlights
        5. Follow-up items or next steps
        6. Overall assessment/recommendation
        
        Format as structured data focusing on concrete details.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse response into structured format
            insights = {
                'technical_skills': [],
                'soft_skills': [],
                'concerns': [],
                'highlights': [],
                'follow_up': [],
                'assessment': ""
            }
            
            # Simple parsing - could be enhanced
            response_text = response.text
            sections = response_text.split('\n\n')
            
            for section in sections:
                if 'technical' in section.lower():
                    insights['technical_skills'].append(section)
                elif 'concern' in section.lower() or 'flag' in section.lower():
                    insights['concerns'].append(section)
                # ... etc
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting interview insights: {e}")
            return {'error': str(e)}
    
    def _combine_interview_insights(self, sessions: List[Dict]) -> str:
        """Combine insights from multiple interview sessions"""
        
        combined = []
        
        combined.append("INTERVIEW INSIGHTS SUMMARY:")
        combined.append("-" * 30)
        
        # Aggregate by type
        all_technical = []
        all_concerns = []
        all_highlights = []
        
        for session in sessions:
            insights = session.get('insights', {})
            all_technical.extend(insights.get('technical_skills', []))
            all_concerns.extend(insights.get('concerns', []))
            all_highlights.extend(insights.get('highlights', []))
        
        if all_technical:
            combined.append("\nTechnical Skills Discussed:")
            for skill in all_technical[:5]:  # Top 5
                combined.append(f"• {skill}")
        
        if all_highlights:
            combined.append("\nPositive Highlights:")
            for highlight in all_highlights[:5]:
                combined.append(f"• {highlight}")
        
        if all_concerns:
            combined.append("\nConcerns Noted:")
            for concern in all_concerns[:3]:  # Top 3
                combined.append(f"• {concern}")
        
        return '\n'.join(combined)
    
    def _extract_work_history(self, text: str) -> List[str]:
        """Extract work history from resume text"""
        # Implementation
        return []
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Implementation
        return []
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume text"""
        # Implementation
        return []
    
    def _extract_equipment(self, text: str) -> List[str]:
        """Extract equipment experience from resume text"""
        # Implementation
        return []
    
    def _convert_pdf_to_images(self, pdf_path: str, output_dir: str):
        """Convert PDF pages to images with enhanced resolution and contrast"""
        try:
            import fitz  # PyMuPDF
            from PIL import Image, ImageEnhance
            
            # Open PDF
            pdf_doc = fitz.open(pdf_path)
            
            # Convert each page to image
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                
                # Render page to image with MUCH higher resolution
                pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))  # 4x scale for better detection
                
                # Save temporary high-res image
                temp_path = os.path.join(output_dir, f"temp_page_{page_num + 1}.png")
                pix.save(temp_path)
                
                # Open with PIL for enhancement
                img = Image.open(temp_path)
                
                # Enhance contrast to make subtle selections more visible
                enhancer = ImageEnhance.Contrast(img)
                img_enhanced = enhancer.enhance(1.5)  # Increase contrast
                
                # Enhance sharpness
                sharpness = ImageEnhance.Sharpness(img_enhanced)
                img_enhanced = sharpness.enhance(2.0)  # Sharpen image
                
                # Save enhanced image
                output_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
                img_enhanced.save(output_path, 'PNG', quality=100)
                
                # Clean up temp file
                os.remove(temp_path)
                
                logger.info(f"Converted PDF page {page_num + 1} to {output_path} with 4x resolution and enhancement")
            
            pdf_doc.close()
            
            # Clean up original PDF
            os.unlink(pdf_path)
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise