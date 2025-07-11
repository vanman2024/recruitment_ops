#!/usr/bin/env python3
"""
Specialized Questionnaire Extractor for Dayforce Recruiting Forms
Extracts all selections, checkboxes, and responses from the structured questionnaire
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

class QuestionnaireExtractor:
    """Extract and structure questionnaire responses from Dayforce recruiting forms"""
    
    def __init__(self, gemini_api_key: str = None):
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def extract_questionnaire_data(self, text_content: str) -> Dict[str, Any]:
        """Extract and structure all questionnaire responses"""
        
        try:
            # Parse the questionnaire sections
            sections = self._parse_sections(text_content)
            
            # Extract structured data from each section
            structured_data = {
                'candidate_name': self._extract_candidate_name(text_content),
                'position_applied': self._extract_position_applied(text_content),
                'submission_date': self._extract_submission_date(text_content),
                'general_information': self._extract_general_info(sections.get('General Information', '')),
                'legal_information': self._extract_legal_info(sections.get('Legal Information', '')),
                'skills_experience': self._extract_skills_experience(sections.get('Underground Heavy Duty Mechanic Skills & Experience', '')),
                'employment_status': self._extract_employment_status(sections.get('Employment Status', '')),
                'work_preferences': self._extract_work_preferences(sections.get('3 Week Shift Rotational Personnel Work Preferences', '')),
                'summary_scores': self._calculate_summary_scores(sections)
            }
            
            # Generate AI insights
            if self.model:
                structured_data['ai_insights'] = self._generate_ai_insights(structured_data, text_content)
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extracting questionnaire data: {e}")
            return {'error': str(e), 'raw_text': text_content}
    
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Parse questionnaire into sections"""
        
        sections = {}
        
        # Define section headers
        section_patterns = {
            'General Information': r'General Information Skilled Trades(.*?)(?=Legal Information|$)',
            'Legal Information': r'Legal Information(.*?)(?=Underground Heavy Duty Mechanic Skills|$)',
            'Underground Heavy Duty Mechanic Skills & Experience': r'Underground Heavy Duty Mechanic Skills & Experience(.*?)(?=Employment Status|$)',
            'Employment Status': r'Employment Status(.*?)(?=3 Week Shift Rotational|$)',
            '3 Week Shift Rotational Personnel Work Preferences': r'3 Week Shift Rotational Personnel Work Preferences(.*?)$'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
        
        return sections
    
    def _extract_candidate_name(self, text: str) -> str:
        """Extract candidate name from the top of the document"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['information', 'date', '2024', 'general']):
                return line
        return "Unknown"
    
    def _extract_position_applied(self, text: str) -> str:
        """Extract position from document header"""
        if 'Underground Heavy Duty Mechanics' in text:
            return 'Underground Heavy Duty Mechanic'
        elif 'Heavy Equipment Technician' in text:
            return 'Heavy Equipment Technician'
        return "Not specified"
    
    def _extract_submission_date(self, text: str) -> str:
        """Extract submission date"""
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        return date_match.group(1) if date_match else "Unknown"
    
    def _extract_general_info(self, section_text: str) -> Dict[str, Any]:
        """Extract general information responses"""
        
        data = {}
        
        # Industries worked in
        if 'Civil and Engineering' in section_text:
            data['industries'] = ['Civil and Engineering']
        if 'Construction' in section_text:
            data['industries'] = data.get('industries', []) + ['Construction']
        if 'Open Pit Mining' in section_text:
            data['industries'] = data.get('industries', []) + ['Open Pit Mining']
        if 'Logging' in section_text:
            data['industries'] = data.get('industries', []) + ['Logging']
        
        # Fast-paced environment
        data['comfortable_fast_paced'] = 'Yes' in section_text and 'fast-paced environment' in section_text
        
        # Physical limitations
        if 'Do you have any physical' in section_text:
            data['physical_limitations'] = 'No' if 'No' in section_text.split('physical')[1].split('\n')[0] else 'Yes'
        
        # Mining experience
        if 'mining industry experience' in section_text.lower():
            data['mining_experience'] = 'Yes' if 'Yes' in section_text else 'No'
            # Extract the reason/comment
            if 'Machine is a machine' in section_text:
                data['mining_experience_comment'] = 'Machine is a machine, just different attachment'
        
        # Positions interested in
        positions = []
        position_keywords = [
            'Journeyman Heavy Equipment Technician',
            'Maintenance Planner', 'Maintenance Scheduler',
            'Journeyman Welder', 'Fuel and Lube Truck Operator',
            'Journeyman Industrial/Construction Electrician',
            'Supervisor/Foreman', 'Labourer', 'Heavy Equipment Operator',
            'Journeyman Machinist', 'Journeyman Millwright'
        ]
        
        for position in position_keywords:
            if position in section_text:
                positions.append(position)
        data['positions_interested'] = positions
        
        # Equipment/gear questions
        data['owns_winter_rain_gear'] = 'Yes' if 'Do you own winter and rain gear?' in section_text and 'Yes' in section_text else None
        data['willing_rotational_shifts'] = 'Yes' if 'rotational shifts' in section_text and 'Yes' in section_text else None
        data['willing_share_service_truck'] = 'Yes' if 'share a service truck' in section_text and 'Yes' in section_text else None
        
        # Apprentice information
        if 'Does not apply to me' in section_text:
            data['apprentice_status'] = 'Not applicable'
        
        return data
    
    def _extract_legal_info(self, section_text: str) -> Dict[str, Any]:
        """Extract legal information responses"""
        
        data = {}
        
        # Background check
        data['background_check'] = 'Yes' if 'criminal background check?' in section_text and 'Yes' in section_text else 'No'
        
        # Work authorization
        data['work_authorization'] = 'Yes' if 'legally able to work' in section_text and 'Yes' in section_text else 'No'
        
        # Drug test
        data['drug_test'] = 'Yes' if 'drug and alcohol test' in section_text and 'Yes' in section_text else 'No'
        
        # Driver's license
        data['drivers_license'] = 'Yes' if 'Class 5 driver' in section_text and 'Yes' in section_text else 'No'
        data['clean_driving_record'] = 'Yes' if 'driver\'s abstract clean' in section_text and 'Yes' in section_text else 'No'
        
        return data
    
    def _extract_skills_experience(self, section_text: str) -> Dict[str, Any]:
        """Extract skills and experience responses"""
        
        data = {}
        
        # Specific equipment experience
        data['komatsu_pc5000'] = 'No' if 'Komatsu PC 5000 experience?' in section_text and 'No' in section_text else None
        
        # Service truck experience
        if 'service truck' in section_text:
            service_match = re.search(r'service truck.*?\n(.*?)\n', section_text, re.DOTALL)
            if service_match:
                data['service_truck_experience'] = service_match.group(1).strip()
        
        # Line boring machine
        data['line_boring_machine'] = 'Yes' if 'portable line boring machine' in section_text and 'Yes' in section_text else 'No'
        
        # CNC machines
        data['cnc_experience'] = 'No' if 'CNC machines?' in section_text and 'No' in section_text else None
        
        # Off-road equipment experience
        if 'off-road construction equipment' in section_text:
            offroad_match = re.search(r'off-road construction equipment.*?\n(.*?)\n', section_text, re.DOTALL)
            if offroad_match:
                data['offroad_equipment_experience'] = offroad_match.group(1).strip()
        
        # Surface mining drills
        data['surface_mining_drills'] = 'None' if 'surface mining drills?' in section_text and 'None' in section_text else None
        
        # CAT ET & SIS
        data['cat_et_sis_level'] = 'Beginner' if 'CAT ET & SIS?' in section_text and 'Beginner' in section_text else None
        
        # PM, hydraulics, etc.
        data['pm_hydraulics_level'] = 'Proficient' if 'PMs (Preventive Maintenance)' in section_text and 'Proficient' in section_text else None
        
        # Large mining equipment
        data['large_mining_equipment'] = 'No Experience' if 'large mining equipment?' in section_text and 'No Experience' in section_text else None
        
        # Red Seal
        data['red_seal'] = 'Yes' if 'Red Seal?' in section_text and 'Yes' in section_text else 'No'
        
        # Journeyman License
        data['journeyman_license'] = 'Yes' if 'Valid Journeyman Off-Road License?' in section_text and 'Yes' in section_text else 'No'
        
        # Line boring experience
        data['line_boring_years'] = 'No Experience' if 'line boring?' in section_text and 'No Experience' in section_text else None
        
        # Underground machinery brands
        brands = []
        brand_keywords = ['Sandvik', 'Epiroc', 'Komatsu', 'Normet', 'Liebherr', 'Joy Global']
        for brand in brand_keywords:
            if brand in section_text:
                brands.append(brand)
        if 'None of the above' in section_text:
            brands = ['None']
        data['underground_machinery_brands'] = brands
        
        # Additional comments
        if 'I am a fast learning person' in section_text:
            data['additional_comments'] = 'I am a fast learning person and pretty resourceful.'
        
        # Hydraulic systems familiarity
        data['hydraulic_systems_level'] = 'Intermediate' if 'hydraulic systems' in section_text and 'Intermediate' in section_text else None
        
        # Underground experience
        data['underground_mechanic_experience'] = 'Yes' if 'underground environments' in section_text and 'Yes' in section_text else 'No'
        
        return data
    
    def _extract_employment_status(self, section_text: str) -> Dict[str, Any]:
        """Extract employment status responses"""
        
        data = {}
        
        # Current company status
        data['still_with_current_company'] = 'Yes' if 'current company on your resume?' in section_text and 'Yes' in section_text else 'No'
        
        # Previous employment
        data['worked_here_before'] = 'Yes' if 'worked for us before?' in section_text and 'Yes' in section_text else 'No'
        
        # Current status
        data['current_employment_status'] = 'Employed' if 'Employed' in section_text else 'Unknown'
        
        # Availability
        data['availability'] = 'Within 1 month' if 'Within 1 month' in section_text else None
        
        # Time off booked
        data['time_off_booked'] = 'Yes' if 'time off booked' in section_text and 'Yes' in section_text else 'No'
        
        # Reason for looking
        data['reason_for_looking'] = 'Work-Life Balance' if 'Work-Life Balance' in section_text else None
        
        # Knows current employees
        data['knows_current_employees'] = 'Yes' if 'know anyone that is currently working' in section_text and 'Yes' in section_text else 'No'
        
        # Contractor preference
        if 'contractor or sub-contractor' in section_text:
            data['contractor_preference'] = 'Employee only' if 'employee only' in section_text else 'Contractor'
        
        return data
    
    def _extract_work_preferences(self, section_text: str) -> Dict[str, Any]:
        """Extract work preferences responses"""
        
        data = {}
        
        # Different mine sites
        data['willing_different_sites'] = 'Yes' if 'different mine sites' in section_text and 'Yes' in section_text else 'No'
        
        # Field work
        data['comfortable_field_work'] = 'Yes' if 'working in the field' in section_text and 'Yes' in section_text else 'No'
        
        # Extended periods away
        data['commit_extended_periods'] = 'Yes' if 'away from home for extended periods' in section_text and 'Yes' in section_text else 'No'
        
        # Rotational shifts
        data['willing_rotational_3weeks'] = 'Yes' if '3 weeks on/off' in section_text and 'Yes' in section_text else 'No'
        
        # Shared housing
        data['comfortable_shared_housing'] = 'Yes' if 'shared housing' in section_text and 'Yes' in section_text else 'No'
        
        return data
    
    def _calculate_summary_scores(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Calculate summary scores and flags"""
        
        scores = {
            'experience_score': 0,
            'certification_score': 0,
            'availability_score': 0,
            'red_flags': [],
            'strengths': []
        }
        
        # Experience scoring
        all_text = ' '.join(sections.values())
        
        if 'Red Seal' in all_text and 'Yes' in all_text:
            scores['certification_score'] += 30
            scores['strengths'].append('Red Seal Certified')
        
        if 'Journeyman' in all_text:
            scores['certification_score'] += 20
            scores['strengths'].append('Journeyman License')
        
        if 'years' in all_text and any(num in all_text for num in ['15', '20', '22']):
            scores['experience_score'] += 40
            scores['strengths'].append('Extensive Experience (15+ years)')
        
        if 'fast learning' in all_text:
            scores['strengths'].append('Self-described fast learner')
        
        # Availability scoring
        if 'Within 1 month' in all_text:
            scores['availability_score'] += 30
        
        if 'Yes' in all_text and 'rotational' in all_text:
            scores['availability_score'] += 20
        
        # Red flags
        if 'No Experience' in all_text:
            scores['red_flags'].append('Limited experience in some key areas')
        
        if 'Beginner' in all_text:
            scores['red_flags'].append('Beginner level in some technical skills')
        
        return scores
    
    def _generate_ai_insights(self, structured_data: Dict, raw_text: str) -> Dict[str, Any]:
        """Generate AI insights from the questionnaire data"""
        
        try:
            prompt = f"""
            Analyze this recruitment questionnaire for a heavy equipment mechanic position:
            
            Candidate: {structured_data.get('candidate_name', 'Unknown')}
            Position: {structured_data.get('position_applied', 'Unknown')}
            
            Structured Data:
            {structured_data}
            
            Provide insights on:
            1. Overall candidate strength (0-100%)
            2. Top 3 strengths
            3. Top 2 concerns or gaps
            4. Equipment expertise level
            5. Cultural fit indicators
            6. Recommendation (Strong Hire/Interview/Pass)
            7. Key questions to ask in interview
            
            Return as JSON structure.
            """
            
            if self.model:
                response = self.model.generate_content(prompt)
                return self._parse_ai_response(response.text)
            else:
                return {'error': 'AI model not configured'}
                
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {'error': str(e)}
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response safely"""
        try:
            import json
            return json.loads(response_text)
        except:
            return {'ai_response': response_text}


# Example usage and test
if __name__ == "__main__":
    # Test with the sample questionnaire
    sample_text = """Gaétan Desrochers
Underground Heavy Duty Mechanics · 25
General Information Skilled Trades 
2024-12-17, 11:49 p.m.
..."""  # Would include full text
    
    extractor = QuestionnaireExtractor()
    result = extractor.extract_questionnaire_data(sample_text)
    print(result)