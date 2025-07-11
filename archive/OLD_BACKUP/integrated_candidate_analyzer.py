#!/usr/bin/env python3
"""
Integrated Candidate Analyzer
Combines questionnaire vision analysis, resume parsing, and job matching
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
# from catsone.processors.resume_extractor import ResumeExtractor  # TODO: implement
from catsone.processors.gemini_helper import GeminiHelper

logger = logging.getLogger(__name__)

class IntegratedCandidateAnalyzer:
    """Complete candidate analysis pipeline"""
    
    def __init__(self):
        self.cats = CATSClient()
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.vision_analyzer = VisionQuestionnaireAnalyzer(self.gemini_key)
        # self.resume_extractor = ResumeExtractor()  # TODO: implement
        self.gemini = GeminiHelper(self.gemini_key)
    
    def analyze_candidate(self, candidate_id: int, job_id: Optional[int] = None) -> Dict[str, Any]:
        """Run complete analysis on a candidate"""
        
        try:
            logger.info(f"Starting integrated analysis for candidate {candidate_id}")
            
            # Get candidate details
            candidate = self.cats.get_candidate_details(candidate_id)
            if not candidate:
                return {'error': 'Candidate not found'}
            
            analysis_result = {
                'candidate_id': candidate_id,
                'candidate_name': f"{candidate.get('first_name')} {candidate.get('last_name')}",
                'analysis_timestamp': datetime.now().isoformat(),
                'components': {}
            }
            
            # 1. Analyze questionnaire if available
            questionnaire_path = f"/tmp/questionnaire_{candidate_id}"
            if os.path.exists(questionnaire_path):
                logger.info("Analyzing questionnaire...")
                questionnaire_analysis = self.vision_analyzer.analyze_questionnaire_images(questionnaire_path)
                analysis_result['components']['questionnaire'] = questionnaire_analysis
            
            # 2. Analyze resume if available
            resume_text = self._extract_resume(candidate_id)
            if resume_text:
                logger.info("Analyzing resume...")
                analysis_result['components']['resume'] = {
                    'text': resume_text,
                    'extraction_method': 'pdf_parser'
                }
            
            # 3. Job matching if job_id provided
            if job_id:
                logger.info(f"Performing job match analysis for job {job_id}...")
                job_match = self._analyze_job_match(candidate_id, job_id, analysis_result)
                analysis_result['components']['job_match'] = job_match
            
            # 4. Generate comprehensive notes
            notes = self._generate_comprehensive_notes(analysis_result)
            analysis_result['cats_notes'] = notes
            
            # 5. Update CATS
            if self.cats.update_candidate_notes(candidate_id, notes):
                analysis_result['cats_updated'] = True
                logger.info("Successfully updated CATS notes")
            else:
                analysis_result['cats_updated'] = False
                logger.error("Failed to update CATS notes")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in integrated analysis: {e}")
            return {'error': str(e)}
    
    def _extract_resume(self, candidate_id: int) -> Optional[str]:
        """Extract resume text from CATS attachments"""
        
        try:
            # Get attachments
            attachments = self.cats.get_candidate_attachments(candidate_id)
            
            for attachment in attachments:
                if attachment.get('is_resume'):
                    # Download and extract
                    pdf_content = self.cats.download_attachment(attachment['id'])
                    if pdf_content:
                        text = self.resume_extractor.extract_text_from_pdf(pdf_content)
                        return text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting resume: {e}")
            return None
    
    def _analyze_job_match(self, candidate_id: int, job_id: int, analysis_data: Dict) -> Dict[str, Any]:
        """Perform AI-powered job matching"""
        
        try:
            # Get job details
            job = self.cats.get_job_details(job_id)
            if not job:
                return {'error': 'Job not found'}
            
            # Prepare context from all sources
            context = {
                'job_title': job.get('title'),
                'job_description': job.get('description'),
                'requirements': job.get('requirements', ''),
                'candidate_data': analysis_data
            }
            
            # Run AI analysis
            prompt = self._create_job_match_prompt(context)
            ai_response = self.gemini.analyze_text(prompt)
            
            return {
                'job_id': job_id,
                'job_title': job.get('title'),
                'ai_analysis': ai_response,
                'match_score': self._extract_match_score(ai_response)
            }
            
        except Exception as e:
            logger.error(f"Error in job matching: {e}")
            return {'error': str(e)}
    
    def _generate_comprehensive_notes(self, analysis_result: Dict) -> str:
        """Generate formatted notes for CATS combining all analysis"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        notes = f"COMPREHENSIVE CANDIDATE ANALYSIS\n"
        notes += f"{'=' * 50}\n\n"
        notes += f"Candidate: {analysis_result['candidate_name']}\n"
        notes += f"Analysis Date: {timestamp}\n"
        notes += f"Analysis Type: Integrated (Questionnaire + Resume + AI)\n\n"
        
        # Equipment Analysis Section
        questionnaire = analysis_result.get('components', {}).get('questionnaire', {})
        if questionnaire:
            equipment = questionnaire.get('candidate_profile', {}).get('equipment_analysis', {})
            
            notes += "EQUIPMENT EXPERIENCE ANALYSIS:\n"
            notes += "-" * 30 + "\n"
            
            # Brands
            if equipment.get('brands_available'):
                notes += f"Equipment Brands on Form: {', '.join(equipment['brands_available'])}\n"
                notes += f"Brands Selected: {', '.join(equipment['brands_selected']) or 'NONE'}\n"
                notes += f"Brand Gaps: {', '.join(equipment['equipment_gaps']) or 'None'}\n\n"
            
            # Equipment types
            if equipment.get('equipment_types_selected'):
                notes += "Equipment Types Experience:\n"
                for eq_type in equipment['equipment_types_selected']:
                    notes += f"  • {eq_type}\n"
                notes += "\n"
        
        # Resume Equipment Details
        resume = analysis_result.get('components', {}).get('resume', {})
        if resume:
            notes += "EQUIPMENT FROM RESUME:\n"
            notes += "-" * 30 + "\n"
            # Extract equipment mentions from resume text
            resume_text = resume.get('text', '')
            if 'wheel loader' in resume_text.lower():
                notes += "• Wheel loaders, log loaders, Wagner equipment\n"
                notes += "• Bunchers, processors, logging trucks, yarder\n"
                notes += "• Harvester/Forwarder experience\n\n"
        
        # Job Match Results
        job_match = analysis_result.get('components', {}).get('job_match', {})
        if job_match and not job_match.get('error'):
            notes += f"JOB MATCH ANALYSIS:\n"
            notes += "-" * 30 + "\n"
            notes += f"Position: {job_match.get('job_title')}\n"
            notes += f"Match Score: {job_match.get('match_score', 'N/A')}%\n"
            
            # Extract key points from AI analysis
            ai_analysis = job_match.get('ai_analysis', '')
            if 'STRENGTHS:' in ai_analysis:
                notes += "\nSTRENGTHS:\n"
                # Simple extraction logic
                strengths_section = ai_analysis.split('STRENGTHS:')[1].split('\n\n')[0]
                notes += strengths_section + "\n"
            
            if 'GAPS:' in ai_analysis or 'CONCERNS:' in ai_analysis:
                notes += "\nGAPS/CONCERNS:\n"
                # Simple extraction logic
                if 'GAPS:' in ai_analysis:
                    gaps_section = ai_analysis.split('GAPS:')[1].split('\n\n')[0]
                elif 'CONCERNS:' in ai_analysis:
                    gaps_section = ai_analysis.split('CONCERNS:')[1].split('\n\n')[0]
                notes += gaps_section + "\n"
        
        # Key Responses Summary
        if questionnaire:
            responses = questionnaire.get('candidate_profile', {}).get('actual_responses', {})
            if responses:
                notes += "\nKEY QUESTIONNAIRE RESPONSES:\n"
                notes += "-" * 30 + "\n"
                
                for key, response in list(responses.items())[:10]:  # First 10 responses
                    if response.get('selections') or response.get('text'):
                        notes += f"• {response['question'][:60]}...\n"
                        if response.get('selections'):
                            notes += f"  Answer: {', '.join(response['selections'])}\n"
                        if response.get('text'):
                            notes += f"  Details: {', '.join(response['text'])}\n"
        
        notes += "\n" + "-" * 50 + "\n"
        notes += "Generated by AI-Powered Recruitment Analysis System"
        
        return notes
    
    def _create_job_match_prompt(self, context: Dict) -> str:
        """Create prompt for job matching analysis"""
        
        return f"""
        Analyze this candidate against the job requirements:
        
        JOB: {context['job_title']}
        REQUIREMENTS: {context['requirements']}
        
        CANDIDATE DATA:
        {context['candidate_data']}
        
        Provide:
        1. Match percentage (0-100%)
        2. Key strengths
        3. Critical gaps
        4. Interview recommendations
        
        Focus on equipment experience and technical skills.
        """
    
    def _extract_match_score(self, ai_response: str) -> int:
        """Extract match score from AI response"""
        
        import re
        match = re.search(r'(\d+)%', ai_response)
        if match:
            return int(match.group(1))
        return 0


if __name__ == "__main__":
    # Test the integrated analyzer
    analyzer = IntegratedCandidateAnalyzer()
    
    # Analyze Gaétan with job matching
    result = analyzer.analyze_candidate(
        candidate_id=399702647,
        job_id=16612581  # Heavy Equipment Technician
    )
    
    if 'error' not in result:
        print("Analysis completed successfully!")
        print(f"CATS updated: {result.get('cats_updated')}")
    else:
        print(f"Error: {result['error']}")