#!/usr/bin/env python3
"""
Integrated Processing Pipeline
Combines document processing, vision analysis, and CATS notes updating
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
from .cats_notes_updater import CATSNotesUpdater
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class IntegratedCandidateProcessor:
    """Complete candidate processing pipeline with CATS integration"""
    
    def __init__(self, cats_api_key: str, cats_api_url: str, gemini_api_key: str):
        self.cats_api_key = cats_api_key
        self.cats_api_url = cats_api_url
        self.gemini_api_key = gemini_api_key
        
        # Initialize processors
        self.document_processor = DocumentProcessor(gemini_api_key)
        self.vision_analyzer = VisionQuestionnaireAnalyzer(gemini_api_key)
        self.notes_updater = CATSNotesUpdater(cats_api_key, cats_api_url)
    
    async def process_candidate_complete(self, candidate_id: int) -> Dict[str, Any]:
        """Complete candidate processing with CATS notes update"""
        
        processing_start = datetime.now()
        results = {
            'candidate_id': candidate_id,
            'processing_start': processing_start.isoformat(),
            'stages_completed': [],
            'errors': []
        }
        
        try:
            # Stage 1: Document retrieval and processing
            logger.info(f"Starting document processing for candidate {candidate_id}")
            doc_result = await self.document_processor.process_candidate_documents(candidate_id)
            
            if 'error' in doc_result:
                results['errors'].append(f"Document processing: {doc_result['error']}")
                return results
            
            results['document_analysis'] = doc_result
            results['stages_completed'].append('document_processing')
            
            # Stage 2: Vision-based questionnaire analysis (if questionnaires found)
            questionnaire_analysis = None
            questionnaires = doc_result.get('documents', {}).get('questionnaires', [])
            
            if questionnaires:
                logger.info(f"Processing {len(questionnaires)} questionnaires with vision analysis")
                
                # For now, process the first questionnaire
                # TODO: Handle multiple questionnaires
                first_questionnaire = questionnaires[0]
                questionnaire_path = first_questionnaire.get('local_path')
                
                if questionnaire_path:
                    # Convert PDF to images and analyze
                    image_folder = await self._convert_pdf_to_images(questionnaire_path)
                    if image_folder:
                        questionnaire_analysis = self.vision_analyzer.analyze_questionnaire_images(image_folder)
                        results['questionnaire_analysis'] = questionnaire_analysis
                        results['stages_completed'].append('questionnaire_analysis')
            
            # Stage 3: Combine all analyses
            combined_analysis = self._combine_analyses(doc_result, questionnaire_analysis)
            results['combined_analysis'] = combined_analysis
            results['stages_completed'].append('analysis_combination')
            
            # Stage 4: Send formatted notes to CATS
            if questionnaire_analysis and 'error' not in questionnaire_analysis:
                logger.info(f"Sending analysis to CATS notes for candidate {candidate_id}")
                notes_result = self.notes_updater.update_candidate_with_analysis(
                    candidate_id, questionnaire_analysis
                )
                results['cats_notes_update'] = notes_result
                
                if notes_result.get('success'):
                    results['stages_completed'].append('cats_notes_update')
                else:
                    results['errors'].append(f"CATS notes update: {notes_result.get('error')}")
            
            # Final timing
            processing_end = datetime.now()
            results['processing_end'] = processing_end.isoformat()
            results['total_time_seconds'] = (processing_end - processing_start).total_seconds()
            results['success'] = len(results['errors']) == 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error in integrated processing: {e}")
            results['errors'].append(f"Pipeline error: {str(e)}")
            results['success'] = False
            return results
    
    async def _convert_pdf_to_images(self, pdf_path: str) -> Optional[str]:
        """Convert PDF to images for vision analysis"""
        
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import os
            
            # Create images directory
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            image_folder = f"questionnaire_images_{base_name}"
            os.makedirs(image_folder, exist_ok=True)
            
            # Convert PDF pages to images
            pdf_doc = fitz.open(pdf_path)
            
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]
                
                # Render page as image (high resolution for better OCR)
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Save as PNG
                image_path = os.path.join(image_folder, f"page_{page_num + 1}.png")
                pix.save(image_path)
            
            pdf_doc.close()
            return image_folder
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return None
    
    def _combine_analyses(self, doc_analysis: Dict, questionnaire_analysis: Optional[Dict]) -> Dict[str, Any]:
        """Combine document and questionnaire analyses"""
        
        combined = {
            'candidate_summary': {},
            'key_findings': [],
            'recommendations': [],
            'analysis_confidence': 'medium'
        }
        
        # Extract from document analysis
        documents = doc_analysis.get('documents', {})
        
        if documents.get('resumes'):
            combined['key_findings'].append(f"Resume analyzed: {len(documents['resumes'])} document(s)")
        
        if documents.get('interview_notes'):
            combined['key_findings'].append(f"Interview notes: {len(documents['interview_notes'])} document(s)")
            combined['analysis_confidence'] = 'high'  # Enhanced with interview
        
        # Extract from questionnaire analysis
        if questionnaire_analysis and 'candidate_profile' in questionnaire_analysis:
            profile = questionnaire_analysis['candidate_profile']
            
            # Key qualifications
            summary = profile.get('response_summary', {})
            if summary.get('key_qualifications'):
                combined['candidate_summary']['qualifications'] = summary['key_qualifications']
            
            if summary.get('experience_highlights'):
                combined['candidate_summary']['experience'] = summary['experience_highlights']
            
            if summary.get('work_preferences'):
                combined['candidate_summary']['preferences'] = summary['work_preferences']
            
            if summary.get('potential_concerns'):
                combined['candidate_summary']['concerns'] = summary['potential_concerns']
                combined['recommendations'].append("Review potential concerns before proceeding")
        
        # Generate recommendations
        if combined['analysis_confidence'] == 'high':
            combined['recommendations'].append("Comprehensive analysis complete - proceed with confidence")
        else:
            combined['recommendations'].append("Consider obtaining interview notes for enhanced analysis")
        
        return combined


# Test the integrated pipeline
if __name__ == "__main__":
    import asyncio
    
    # Get credentials
    cats_api_key = os.getenv('CATS_API_KEY')
    cats_api_url = os.getenv('CATS_API_URL')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not all([cats_api_key, cats_api_url, gemini_api_key]):
        print("Missing required API credentials")
        exit(1)
    
    # Create processor
    processor = IntegratedCandidateProcessor(cats_api_key, cats_api_url, gemini_api_key)
    
    # Test with sample candidate ID
    async def test_pipeline():
        candidate_id = 12345  # Replace with real candidate ID
        result = await processor.process_candidate_complete(candidate_id)
        
        print("=== INTEGRATED PIPELINE RESULT ===")
        print(f"Candidate: {result['candidate_id']}")
        print(f"Success: {result['success']}")
        print(f"Stages: {', '.join(result['stages_completed'])}")
        print(f"Processing time: {result.get('total_time_seconds', 0):.1f}s")
        
        if result.get('errors'):
            print(f"Errors: {result['errors']}")
        
        if result.get('combined_analysis'):
            analysis = result['combined_analysis']
            print(f"Analysis confidence: {analysis.get('analysis_confidence')}")
            print(f"Key findings: {analysis.get('key_findings')}")
    
    # Note: Uncomment to run actual test
    # asyncio.run(test_pipeline())
    print("Integrated pipeline ready - uncomment test to run")