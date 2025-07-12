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
from catsone.processors.pillow_form_enhancer import PillowFormEnhancer
from catsone.processors.pdf_form_extractor import PDFFormExtractor
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
        
        # Initialize enhanced processing components
        self.form_enhancer = PillowFormEnhancer()
        self.pdf_extractor = PDFFormExtractor()
    
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
        """Process questionnaire attachment(s) using hybrid approach"""
        
        try:
            results = {
                'pdf_extraction': None,
                'vision_analysis': None,
                'hybrid_result': None,
                'confidence_score': 0.0
            }
            
            # First, try PDF form extraction for any PDF files
            pdf_results = self._extract_pdf_forms(questionnaire_info)
            if pdf_results.get('has_form_fields'):
                results['pdf_extraction'] = pdf_results
                logger.info("Successfully extracted PDF form fields")
            
            # Then, do enhanced vision analysis
            vision_results = self._enhanced_vision_analysis(questionnaire_info)
            results['vision_analysis'] = vision_results
            
            # Combine results using hybrid approach
            results['hybrid_result'] = self._combine_extraction_results(
                pdf_results, vision_results
            )
            
            # Calculate confidence score
            results['confidence_score'] = self._calculate_confidence(results)
            
            # Apply Dayforce handler if needed
            is_dayforce = self._detect_dayforce(questionnaire_info)
            if is_dayforce:
                results['hybrid_result'] = self.dayforce_handler.process_dayforce_questionnaire(
                    results['hybrid_result']
                )
            
            return results
                
        except Exception as e:
            logger.error(f"Error processing questionnaire: {e}")
            return {'error': str(e)}
    
    def _extract_pdf_forms(self, questionnaire_info: Dict) -> Dict[str, Any]:
        """Extract form fields directly from PDF files"""
        
        combined_data = {'has_form_fields': False}
        
        try:
            # Get all PDF attachments
            for attachment in questionnaire_info.get('attachments', []):
                file_path = self._download_attachment(attachment['id'])
                
                if file_path and file_path.endswith('.pdf'):
                    # Try direct PDF form extraction
                    pdf_data = self.pdf_extractor.extract_all_fields(file_path)
                    
                    if pdf_data.get('has_form_fields'):
                        combined_data = pdf_data
                        logger.info(f"Extracted form fields from {attachment.get('filename', 'PDF')}")
                    
                    # Clean up
                    os.unlink(file_path)
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error extracting PDF forms: {e}")
            return {'has_form_fields': False, 'error': str(e)}
    
    def _enhanced_vision_analysis(self, questionnaire_info: Dict) -> Dict[str, Any]:
        """Perform enhanced vision analysis with Pillow preprocessing"""
        
        try:
            # Create enhanced versions for better detection
            temp_folder = tempfile.mkdtemp()
            enhanced_folder = tempfile.mkdtemp()
            
            # Download and process images
            if questionnaire_info['type'] == 'multi_page':
                for i, page_info in enumerate(questionnaire_info['pages']):
                    file_path = self._download_attachment(page_info['id'])
                    if file_path:
                        new_path = os.path.join(temp_folder, f"page_{i+1}.png")
                        os.rename(file_path, new_path)
            else:
                for attachment in questionnaire_info.get('attachments', []):
                    file_path = self._download_attachment(attachment['id'])
                    if file_path:
                        if file_path.endswith('.pdf'):
                            self._convert_pdf_to_images(file_path, temp_folder)
                        else:
                            import shutil
                            shutil.move(file_path, os.path.join(temp_folder, 'page_1.png'))
            
            # Create enhanced versions of all images
            enhanced_paths = {}
            for img_file in os.listdir(temp_folder):
                if img_file.endswith('.png'):
                    img_path = os.path.join(temp_folder, img_file)
                    enhanced_versions = self.form_enhancer.create_enhanced_versions(img_path)
                    
                    # Save enhanced versions
                    base_name = os.path.splitext(img_file)[0]
                    for version_name, enhanced_img in enhanced_versions.items():
                        enhanced_path = os.path.join(enhanced_folder, f"{base_name}_{version_name}.png")
                        enhanced_img.save(enhanced_path, 'PNG', quality=100)
                        
                        if version_name not in enhanced_paths:
                            enhanced_paths[version_name] = []
                        enhanced_paths[version_name].append(enhanced_path)
            
            # Run vision analysis on both original and enhanced versions
            results = {}
            
            # Original analysis
            original_result = self.vision_analyzer.analyze_questionnaire_images(temp_folder)
            results['original'] = original_result
            
            # Enhanced analyses
            for version_name, image_paths in enhanced_paths.items():
                if version_name in ['checkbox_binary', 'radio_enhanced', 'combined']:
                    # Create temp folder for this version
                    version_folder = tempfile.mkdtemp()
                    
                    # Copy enhanced images to version folder
                    for i, img_path in enumerate(image_paths):
                        import shutil
                        dest_path = os.path.join(version_folder, f"page_{i+1}.png")
                        shutil.copy2(img_path, dest_path)
                    
                    # Analyze this version
                    version_result = self.vision_analyzer.analyze_questionnaire_images(version_folder)
                    results[version_name] = version_result
                    
                    # Clean up version folder
                    shutil.rmtree(version_folder)
            
            # Clean up temp folders
            import shutil
            shutil.rmtree(temp_folder)
            shutil.rmtree(enhanced_folder)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in enhanced vision analysis: {e}")
            return {'error': str(e)}
    
    def _combine_extraction_results(self, pdf_data: Dict, vision_data: Dict) -> Dict[str, Any]:
        """Combine PDF and vision extraction results intelligently"""
        
        combined = {
            'extraction_method': 'hybrid',
            'pdf_available': pdf_data.get('has_form_fields', False),
            'vision_versions': list(vision_data.keys()) if vision_data else [],
            'final_data': {}
        }
        
        try:
            # If PDF extraction was successful, use it as the base
            if pdf_data.get('has_form_fields') and pdf_data.get('questionnaire_data'):
                combined['final_data'] = pdf_data['questionnaire_data'].copy()
                combined['primary_source'] = 'pdf'
                logger.info("Using PDF extraction as primary source")
            else:
                combined['primary_source'] = 'vision'
                logger.info("Using vision analysis as primary source")
            
            # Find the best vision analysis result
            best_vision_result = self._select_best_vision_result(vision_data)
            if best_vision_result:
                combined['best_vision_version'] = best_vision_result['version']
                
                # If no PDF data, use vision as primary
                if not combined['final_data']:
                    combined['final_data'] = best_vision_result['data']
                else:
                    # Cross-validate and fill gaps with vision data
                    self._cross_validate_results(combined['final_data'], best_vision_result['data'])
            
            return combined
            
        except Exception as e:
            logger.error(f"Error combining extraction results: {e}")
            return {'error': str(e)}
    
    def _select_best_vision_result(self, vision_data: Dict) -> Optional[Dict]:
        """Select the best vision analysis result based on completeness and confidence"""
        
        if not vision_data:
            return None
        
        best_result = None
        best_score = 0
        
        # Score each version based on data completeness
        for version_name, result in vision_data.items():
            if isinstance(result, dict) and 'extracted_data' in result:
                data = result['extracted_data']
                score = 0
                
                # Score based on key fields extracted
                key_fields = ['red_seal_status', 'trade_licenses', 'years_experience', 
                            'willing_to_travel', 'available_start']
                
                for field in key_fields:
                    if field in data and data[field] not in [None, '', 'Not specified']:
                        score += 1
                
                # Bonus for specialized versions
                if version_name in ['checkbox_binary', 'radio_enhanced']:
                    score += 0.5
                
                if score > best_score:
                    best_score = score
                    best_result = {
                        'version': version_name,
                        'data': data,
                        'score': score
                    }
        
        return best_result
    
    def _cross_validate_results(self, pdf_data: Dict, vision_data: Dict):
        """Cross-validate PDF and vision results, filling gaps"""
        
        # For each field, compare PDF vs Vision and choose the best
        critical_fields = ['red_seal_status', 'trade_licenses', 'years_experience']
        
        for field in critical_fields:
            pdf_value = pdf_data.get(field)
            vision_value = vision_data.get(field)
            
            # If PDF is empty but vision has data, use vision
            if not pdf_value and vision_value:
                pdf_data[field] = vision_value
                logger.info(f"Filled {field} from vision analysis: {vision_value}")
            
            # If values conflict, log for manual review
            elif pdf_value and vision_value and pdf_value != vision_value:
                logger.warning(f"Conflict in {field}: PDF='{pdf_value}' vs Vision='{vision_value}'")
                # For now, keep PDF value but add note
                pdf_data[f'{field}_conflict'] = {
                    'pdf': pdf_value,
                    'vision': vision_value
                }
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calculate overall confidence score for the extraction"""
        
        confidence = 0.0
        
        # Base confidence from extraction methods available
        if results.get('pdf_extraction', {}).get('has_form_fields'):
            confidence += 0.6  # PDF extraction is more reliable
        
        if results.get('vision_analysis'):
            confidence += 0.4  # Vision analysis adds confidence
        
        # Boost confidence if multiple methods agree
        if results.get('hybrid_result', {}).get('primary_source') == 'pdf':
            confidence += 0.2
        
        # Reduce confidence if there are conflicts
        final_data = results.get('hybrid_result', {}).get('final_data', {})
        conflicts = [k for k in final_data.keys() if k.endswith('_conflict')]
        confidence -= len(conflicts) * 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _detect_dayforce(self, questionnaire_info: Dict) -> bool:
        """Detect if this is a Dayforce questionnaire"""
        
        for attachment in questionnaire_info.get('attachments', []):
            filename = attachment.get('filename', '').lower()
            if 'dayforce' in filename:
                logger.info(f"Detected Dayforce questionnaire: {filename}")
                return True
        return False
    
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