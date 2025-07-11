#!/usr/bin/env python3
"""
Complete Questionnaire Extractor - Captures EVERYTHING
Systematically extracts every question and answer from Dayforce questionnaires
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

class CompleteQuestionnaireExtractor:
    """Extract every single question and answer from questionnaires"""
    
    def __init__(self, gemini_api_key: str = None):
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def extract_complete_questionnaire(self, text_content: str) -> Dict[str, Any]:
        """Extract EVERYTHING from the questionnaire systematically"""
        
        try:
            # Parse all questions and answers
            qa_pairs = self._extract_all_qa_pairs(text_content)
            
            # Structure the complete data
            complete_data = {
                'candidate_info': self._extract_candidate_info(text_content),
                'all_questions_answers': qa_pairs,
                'structured_responses': self._structure_responses(qa_pairs),
                'extraction_metadata': {
                    'total_questions': len(qa_pairs),
                    'extraction_timestamp': datetime.now().isoformat(),
                    'extraction_method': 'systematic_parsing'
                }
            }
            
            return complete_data
            
        except Exception as e:
            logger.error(f"Error in complete extraction: {e}")
            return {'error': str(e), 'raw_text': text_content}
    
    def _extract_candidate_info(self, text: str) -> Dict[str, str]:
        """Extract basic candidate information"""
        
        lines = text.split('\n')
        
        # Get candidate name (first non-empty line that's not a header)
        candidate_name = "Unknown"
        for line in lines[:10]:
            line = line.strip()
            if (line and 
                not any(word in line.lower() for word in ['information', 'skilled', 'trades', 'general', 'date', '2024']) and
                len(line) > 2 and len(line) < 50):
                candidate_name = line
                break
        
        # Extract position/role
        position = "Unknown"
        if 'Underground Heavy Duty Mechanics' in text:
            position = 'Underground Heavy Duty Mechanics'
        elif 'Heavy Equipment Technician' in text:
            position = 'Heavy Equipment Technician'
        
        # Extract submission date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        submission_date = date_match.group(1) if date_match else "Unknown"
        
        # Extract time if available
        time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:a\.m\.|p\.m\.))', text)
        submission_time = time_match.group(1) if time_match else "Unknown"
        
        return {
            'name': candidate_name,
            'position_applied': position,
            'submission_date': submission_date,
            'submission_time': submission_time
        }
    
    def _extract_all_qa_pairs(self, text: str) -> List[Dict[str, Any]]:
        """Extract every single question and answer pair"""
        
        qa_pairs = []
        
        # Split text into lines and process
        lines = text.split('\n')
        current_question = None
        current_answer = []
        question_number = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this is a question (starts with number)
            question_match = re.match(r'^(\d+)\s*(.+)', line)
            
            if question_match:
                # Save previous Q&A if exists
                if current_question:
                    qa_pairs.append({
                        'question_number': question_number,
                        'question': current_question,
                        'answer': ' '.join(current_answer).strip(),
                        'answer_lines': current_answer.copy()
                    })
                
                # Start new question
                question_number = int(question_match.group(1))
                current_question = question_match.group(2).strip()
                current_answer = []
                
            elif current_question and line:
                # This is part of an answer or continuation
                # Skip section headers
                if not any(header in line for header in [
                    'General Information', 'Legal Information', 
                    'Skills & Experience', 'Employment Status', 
                    'Work Preferences', '2024-', 'Recruiting'
                ]):
                    current_answer.append(line)
        
        # Add the last Q&A pair
        if current_question:
            qa_pairs.append({
                'question_number': question_number,
                'question': current_question,
                'answer': ' '.join(current_answer).strip(),
                'answer_lines': current_answer.copy()
            })
        
        return qa_pairs
    
    def _structure_responses(self, qa_pairs: List[Dict]) -> Dict[str, Any]:
        """Structure responses into logical categories"""
        
        structured = {
            'general_information': {},
            'legal_clearances': {},
            'technical_skills': {},
            'experience_details': {},
            'employment_status': {},
            'work_preferences': {},
            'certifications': {},
            'equipment_experience': {}
        }
        
        for qa in qa_pairs:
            question = qa['question'].lower()
            answer = qa['answer']
            
            # Categorize and extract specific responses
            if 'industries' in question and 'worked in' in question:
                structured['general_information']['industries_worked'] = self._extract_multiple_choice(answer)
            
            elif 'fast-paced environment' in question:
                structured['general_information']['comfortable_fast_paced'] = 'Yes' in answer
            
            elif 'physical, visual, or auditory limitations' in question:
                structured['general_information']['physical_limitations'] = answer
            
            elif 'mining industry experience' in question:
                structured['experience_details']['mining_experience'] = {
                    'has_experience': 'Yes' in answer,
                    'details': answer
                }
            
            elif 'position' in question and 'interested' in question:
                structured['general_information']['positions_interested'] = self._extract_positions(answer)
            
            elif 'winter and rain gear' in question:
                structured['work_preferences']['owns_weather_gear'] = 'Yes' in answer
            
            elif 'rotational shifts' in question and 'days then' in question:
                structured['work_preferences']['willing_day_night_rotation'] = 'Yes' in answer
            
            elif 'share a service truck' in question:
                structured['work_preferences']['willing_share_truck'] = 'Yes' in answer
            
            elif 'beard' in question and 'clean shaven' in question:
                structured['work_preferences']['beard_policy_compliance'] = answer
            
            elif 'registered apprentice' in question:
                structured['certifications']['apprentice_status'] = answer
            
            elif 'trade are you registered' in question:
                structured['certifications']['apprentice_trade'] = answer
            
            # Legal Information
            elif 'criminal background check' in question:
                structured['legal_clearances']['background_check'] = 'Yes' in answer
            
            elif 'legally able to work' in question:
                structured['legal_clearances']['work_authorization'] = 'Yes' in answer
            
            elif 'drug and alcohol test' in question:
                structured['legal_clearances']['drug_test'] = 'Yes' in answer
            
            elif 'class 5 driver' in question:
                structured['legal_clearances']['drivers_license'] = 'Yes' in answer
            
            elif 'driver\'s abstract clean' in question:
                structured['legal_clearances']['clean_driving_record'] = 'Yes' in answer
            
            # Technical Skills & Experience
            elif 'komatsu pc' in question and '5' in question:
                # Fix the PC 5500 vs PC 5000 issue
                if '5500' in question or '55' in question:
                    structured['equipment_experience']['komatsu_pc5500'] = 'Yes' in answer or 'No' in answer
                else:
                    structured['equipment_experience']['komatsu_pc5000'] = 'Yes' in answer or 'No' in answer
            
            elif 'service truck' in question and 'years' in question:
                structured['experience_details']['service_truck_years'] = answer
            
            elif 'line boring machine' in question:
                structured['technical_skills']['line_boring_machine'] = 'Yes' in answer
            
            elif 'cnc machines' in question:
                structured['technical_skills']['cnc_experience'] = answer
            
            elif 'off-road construction equipment' in question:
                structured['experience_details']['offroad_equipment_experience'] = answer
            
            elif 'surface mining drills' in question:
                structured['experience_details']['surface_mining_drills'] = answer
            
            elif 'cat et & sis' in question:
                structured['technical_skills']['cat_et_sis_level'] = answer
            
            elif 'pms' in question and 'hydraulics' in question:
                structured['technical_skills']['pm_hydraulics_level'] = answer
            
            elif 'large mining equipment' in question:
                structured['experience_details']['large_mining_equipment'] = answer
            
            elif 'red seal' in question:
                structured['certifications']['red_seal'] = 'Yes' in answer
            
            elif 'journeyman off-road license' in question:
                structured['certifications']['journeyman_license'] = 'Yes' in answer
            
            elif 'line boring' in question and 'years' in question:
                structured['experience_details']['line_boring_years'] = answer
            
            elif 'underground machinery brands' in question:
                structured['equipment_experience']['underground_brands'] = self._extract_brands(answer)
            
            elif 'hydraulic systems' in question and 'underground' in question:
                structured['technical_skills']['hydraulic_systems_level'] = answer
            
            elif 'underground environments' in question:
                structured['experience_details']['underground_experience'] = 'Yes' in answer
            
            # Employment Status
            elif 'current company on your resume' in question:
                structured['employment_status']['still_with_current'] = 'Yes' in answer
            
            elif 'worked for us before' in question:
                structured['employment_status']['worked_here_before'] = answer
            
            elif 'current employment status' in question:
                structured['employment_status']['current_status'] = answer
            
            elif 'available to start work' in question:
                structured['employment_status']['availability'] = answer
            
            elif 'time off booked' in question:
                structured['employment_status']['time_off_booked'] = answer
            
            elif 'looking for a new opportunity' in question:
                structured['employment_status']['reason_for_leaving'] = answer
            
            elif 'know anyone that is currently working' in question:
                structured['employment_status']['knows_employees'] = answer
            
            elif 'contractor or sub-contractor' in question:
                structured['employment_status']['contractor_preference'] = answer
            
            # Work Preferences (3-week rotation)
            elif 'different mine sites' in question:
                structured['work_preferences']['willing_different_sites'] = 'Yes' in answer
            
            elif 'working in the field' in question:
                structured['work_preferences']['comfortable_field_work'] = 'Yes' in answer
            
            elif 'away from home for extended periods' in question:
                structured['work_preferences']['commit_extended_periods'] = 'Yes' in answer
            
            elif '3 weeks on/off' in question:
                structured['work_preferences']['willing_3week_rotation'] = 'Yes' in answer
            
            elif 'shared housing' in question:
                structured['work_preferences']['comfortable_shared_housing'] = 'Yes' in answer
        
        return structured
    
    def _extract_multiple_choice(self, answer: str) -> List[str]:
        """Extract multiple choice selections"""
        choices = []
        
        # Common industry options
        industry_options = [
            'Civil and Engineering', 'Construction', 'Open Pit Mining', 
            'Logging', 'Underground Mining', 'Manufacturing'
        ]
        
        for option in industry_options:
            if option in answer:
                choices.append(option)
        
        return choices
    
    def _extract_positions(self, answer: str) -> List[str]:
        """Extract position selections"""
        positions = []
        
        position_options = [
            'Journeyman Heavy Equipment Technician', 'Maintenance Planner',
            'Maintenance Scheduler', 'Journeyman Welder', 'Fuel and Lube Truck Operator',
            'Journeyman Industrial/Construction Electrician', 'Supervisor/Foreman',
            'Labourer', 'Heavy Equipment Operator', 'Sales Representative',
            'Administrative Assistant', 'HR Coordinator', 'Finance and Accounting Professional',
            'Journeyman Machinist', 'Journeyman Millwright'
        ]
        
        for position in position_options:
            if position in answer:
                positions.append(position)
        
        return positions
    
    def _extract_brands(self, answer: str) -> List[str]:
        """Extract equipment brand selections"""
        brands = []
        
        brand_options = [
            'Sandvik', 'Epiroc', 'Komatsu', 'Normet', 'Liebherr', 'Joy Global'
        ]
        
        if 'None of the above' in answer:
            return ['None of the above']
        
        for brand in brand_options:
            if brand in answer:
                brands.append(brand)
        
        return brands
    
    def match_against_job_requirements(self, questionnaire_data: Dict, job_requirements: Dict) -> Dict[str, Any]:
        """Use AI to match candidate against specific job requirements"""
        
        try:
            if not self.model:
                return {'error': 'AI model not configured'}
            
            prompt = f"""
            You are an expert recruitment AI. Analyze this candidate's questionnaire responses against specific job requirements.
            
            CANDIDATE DATA:
            {questionnaire_data}
            
            JOB REQUIREMENTS:
            {job_requirements}
            
            Provide a comprehensive analysis:
            
            1. OVERALL MATCH SCORE (0-100%)
            
            2. REQUIREMENT ANALYSIS:
            - For each job requirement, indicate if candidate meets it (Yes/No/Partial)
            - Provide evidence from questionnaire
            
            3. STRENGTHS:
            - Top 5 candidate strengths relevant to this job
            - Include years of experience, certifications, equipment familiarity
            
            4. GAPS/CONCERNS:
            - Requirements not met or partially met
            - Skills that need development
            - Any red flags
            
            5. EQUIPMENT MATCH:
            - Compare required equipment vs candidate experience
            - Highlight exact matches and learning needs
            
            6. CULTURAL FIT:
            - Work preferences alignment (rotational, remote, etc.)
            - Attitude indicators from responses
            
            7. RECOMMENDATION:
            - Strong Hire / Interview / Pass with reasoning
            - Key interview questions to ask
            - Training needs if hired
            
            8. SALARY RANGE RECOMMENDATION:
            - Based on experience level and certifications
            
            Return as structured JSON for easy parsing.
            """
            
            response = self.model.generate_content(prompt)
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            logger.error(f"Error in job matching: {e}")
            return {'error': str(e)}
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response safely"""
        try:
            import json
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {'ai_analysis': response_text}
        except:
            return {'ai_response': response_text}


# Test with actual questionnaire
if __name__ == "__main__":
    import fitz
    
    # Read the PDF
    doc = fitz.open('/mnt/c/Users/angel/Downloads/Recruiting - Dayforce.pdf')
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    
    # Extract complete data
    extractor = CompleteQuestionnaireExtractor()
    result = extractor.extract_complete_questionnaire(text)
    
    print("=== COMPLETE QUESTIONNAIRE EXTRACTION ===")
    print(f"Candidate: {result['candidate_info']['name']}")
    print(f"Total Questions Extracted: {result['extraction_metadata']['total_questions']}")
    print()
    
    print("=== ALL QUESTIONS & ANSWERS ===")
    for qa in result['all_questions_answers'][:5]:  # Show first 5
        print(f"Q{qa['question_number']}: {qa['question']}")
        print(f"A: {qa['answer']}")
        print()
    
    print("=== STRUCTURED RESPONSES ===")
    for category, data in result['structured_responses'].items():
        if data:
            print(f"{category.upper()}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
            print()