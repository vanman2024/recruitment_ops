#!/usr/bin/env python3
"""
Robust Questionnaire Parser for Dayforce Forms
Handles the specific format and extracts ALL responses systematically
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RobustQuestionnaireParser:
    """Parse Dayforce questionnaires with specific format handling"""
    
    def __init__(self):
        pass
    
    def parse_complete_questionnaire(self, text_content: str) -> Dict[str, Any]:
        """Parse the complete questionnaire using format-specific rules"""
        
        try:
            # Clean and normalize the text
            cleaned_text = self._clean_text(text_content)
            
            # Extract candidate info
            candidate_info = self._extract_candidate_info(cleaned_text)
            
            # Parse all responses using manual extraction
            responses = self._extract_all_responses(cleaned_text)
            
            return {
                'candidate_info': candidate_info,
                'complete_responses': responses,
                'summary': self._create_summary(responses),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing questionnaire: {e}")
            return {'error': str(e)}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize the text for parsing"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n', ' ')
        return text.strip()
    
    def _extract_candidate_info(self, text: str) -> Dict[str, str]:
        """Extract basic candidate information"""
        
        # Extract name (first line typically)
        name_match = re.search(r'^([A-Za-z\s]+)', text)
        name = name_match.group(1).strip() if name_match else "Unknown"
        
        # Extract position
        position = "Unknown"
        if 'Underground Heavy Duty Mechanics' in text:
            position = 'Underground Heavy Duty Mechanics'
        elif 'Heavy Equipment Technician' in text:
            position = 'Heavy Equipment Technician'
        
        # Extract date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        date = date_match.group(1) if date_match else "Unknown"
        
        return {
            'name': name,
            'position': position,
            'date': date
        }
    
    def _extract_all_responses(self, text: str) -> Dict[str, Any]:
        """Extract all responses using manual pattern matching"""
        
        responses = {}
        
        # 1. Industries worked in
        responses['industries_worked'] = []
        if 'Civil and Engineering' in text:
            responses['industries_worked'].append('Civil and Engineering')
        if 'Construction' in text:
            responses['industries_worked'].append('Construction')
        if 'Open Pit Mining' in text:
            responses['industries_worked'].append('Open Pit Mining')
        if 'Logging' in text:
            responses['industries_worked'].append('Logging')
        
        # 2. Fast-paced environment
        fast_paced_match = re.search(r'fast-paced environment.*?(Yes|No)', text, re.IGNORECASE)
        responses['comfortable_fast_paced'] = fast_paced_match.group(1) if fast_paced_match else None
        
        # 3. Physical limitations
        limitations_match = re.search(r'physical.*?limitations.*?(No|Yes.*?)(?:\s|$)', text, re.IGNORECASE)
        responses['physical_limitations'] = limitations_match.group(1) if limitations_match else None
        
        # 4. Mining experience
        mining_match = re.search(r'mining industry experience.*?(Yes|No)', text, re.IGNORECASE)
        responses['mining_experience'] = mining_match.group(1) if mining_match else None
        if 'Machine is a machine' in text:
            responses['mining_experience_comment'] = 'Machine is a machine, just different attachment'
        
        # 5. Positions interested in
        responses['positions_interested'] = []
        positions = [
            'Journeyman Heavy Equipment Technician', 'Maintenance Planner', 'Maintenance Scheduler',
            'Journeyman Welder', 'Fuel and Lube Truck Operator', 'Journeyman Industrial/Construction Electrician',
            'Supervisor/Foreman', 'Labourer', 'Heavy Equipment Operator', 'Sales Representative',
            'Administrative Assistant', 'HR Coordinator', 'Finance and Accounting Professional',
            'Journeyman Machinist', 'Journeyman Millwright'
        ]
        for position in positions:
            if position in text:
                responses['positions_interested'].append(position)
        
        # 6. Winter and rain gear
        gear_match = re.search(r'winter and rain gear.*?(Yes|No)', text, re.IGNORECASE)
        responses['owns_weather_gear'] = gear_match.group(1) if gear_match else None
        
        # 7. Rotational shifts (days/nights)
        rotation_match = re.search(r'rotational shifts.*?days.*?nights.*?(Yes|No)', text, re.IGNORECASE)
        responses['willing_day_night_rotation'] = rotation_match.group(1) if rotation_match else None
        
        # 8. Share service truck
        truck_match = re.search(r'share a service truck.*?(Yes|No)', text, re.IGNORECASE)
        responses['willing_share_truck'] = truck_match.group(1) if truck_match else None
        
        # 9. Beard/clean shaven
        beard_match = re.search(r'beard.*?clean shaven.*?(Does Not Apply|Yes|No)', text, re.IGNORECASE)
        responses['beard_policy'] = beard_match.group(1) if beard_match else None
        
        # 10. Apprentice status
        apprentice_match = re.search(r'registered Apprentice.*?(Does not apply|.*?year)', text, re.IGNORECASE)
        responses['apprentice_status'] = apprentice_match.group(1) if apprentice_match else None
        
        # Legal Information
        # 11. Background check
        bg_match = re.search(r'criminal background check.*?(Yes|No)', text, re.IGNORECASE)
        responses['background_check'] = bg_match.group(1) if bg_match else None
        
        # 12. Work authorization
        auth_match = re.search(r'legally able to work.*?(Yes|No)', text, re.IGNORECASE)
        responses['work_authorization'] = auth_match.group(1) if auth_match else None
        
        # 13. Drug test
        drug_match = re.search(r'drug and alcohol test.*?(Yes|No)', text, re.IGNORECASE)
        responses['drug_test'] = drug_match.group(1) if drug_match else None
        
        # 14. Driver's license
        license_match = re.search(r'Class 5 driver.*?(Yes|No)', text, re.IGNORECASE)
        responses['drivers_license'] = license_match.group(1) if license_match else None
        
        # 15. Clean driving record
        record_match = re.search(r'driver.*?abstract clean.*?(Yes|No)', text, re.IGNORECASE)
        responses['clean_driving_record'] = record_match.group(1) if record_match else None
        
        # Skills & Experience
        # 16. Komatsu PC 5500 (FIXED - was 5000)
        komatsu_match = re.search(r'Komatsu PC.*?55.*?(Yes|No)', text, re.IGNORECASE)
        responses['komatsu_pc5500_experience'] = komatsu_match.group(1) if komatsu_match else None
        
        # 17. Service truck years
        service_truck_match = re.search(r'service truck.*?(Other.*?career.*?\d+.*?years?|.*?years?)', text, re.IGNORECASE)
        responses['service_truck_experience'] = service_truck_match.group(1) if service_truck_match else None
        
        # 18. Line boring machine
        boring_match = re.search(r'portable line boring machine.*?(Yes|No)', text, re.IGNORECASE)
        responses['line_boring_machine'] = boring_match.group(1) if boring_match else None
        
        # 19. CNC machines
        cnc_match = re.search(r'CNC machines.*?(Yes|No)', text, re.IGNORECASE)
        responses['cnc_experience'] = cnc_match.group(1) if cnc_match else None
        
        # 20. Off-road equipment experience
        offroad_match = re.search(r'off-road construction equipment.*?(Other.*?equipment.*?years?|.*?years?)', text, re.IGNORECASE)
        responses['offroad_equipment_experience'] = offroad_match.group(1) if offroad_match else None
        
        # 21. Surface mining drills
        drills_match = re.search(r'surface mining drills.*?(None|.*?years?)', text, re.IGNORECASE)
        responses['surface_mining_drills'] = drills_match.group(1) if drills_match else None
        
        # 22. CAT ET & SIS
        cat_match = re.search(r'CAT ET.*?SIS.*?(Beginner|Intermediate|Advanced|Expert)', text, re.IGNORECASE)
        responses['cat_et_sis_level'] = cat_match.group(1) if cat_match else None
        
        # 23. PMs, hydraulics, troubleshooting
        pm_match = re.search(r'PMs.*?hydraulics.*?troubleshooting.*?(Beginner|Intermediate|Proficient|Expert)', text, re.IGNORECASE)
        responses['pm_hydraulics_level'] = pm_match.group(1) if pm_match else None
        
        # 24. Large mining equipment
        large_equip_match = re.search(r'large mining equipment.*?(No Experience|Beginner|Intermediate|Advanced)', text, re.IGNORECASE)
        responses['large_mining_equipment'] = large_equip_match.group(1) if large_equip_match else None
        
        # 25. Red Seal
        red_seal_match = re.search(r'Red Seal.*?(Yes|No)', text, re.IGNORECASE)
        responses['red_seal'] = red_seal_match.group(1) if red_seal_match else None
        
        # 26. Journeyman license
        journeyman_match = re.search(r'Journeyman Off-Road License.*?(Yes|No)', text, re.IGNORECASE)
        responses['journeyman_license'] = journeyman_match.group(1) if journeyman_match else None
        
        # 27. Line boring years
        boring_years_match = re.search(r'line boring.*?years.*?(No Experience|.*?years?)', text, re.IGNORECASE)
        responses['line_boring_years'] = boring_years_match.group(1) if boring_years_match else None
        
        # 28. Underground machinery brands
        responses['underground_brands'] = []
        brands = ['Sandvik', 'Epiroc', 'Komatsu', 'Normet', 'Liebherr', 'Joy Global']
        for brand in brands:
            if brand in text:
                responses['underground_brands'].append(brand)
        if 'None of the above' in text:
            responses['underground_brands'] = ['None of the above']
        
        # 29. Hydraulic systems level
        hydraulic_match = re.search(r'hydraulic systems.*?underground.*?(Beginner|Intermediate|Advanced|Expert)', text, re.IGNORECASE)
        responses['hydraulic_systems_level'] = hydraulic_match.group(1) if hydraulic_match else None
        
        # 30. Underground experience
        underground_match = re.search(r'underground environments.*?(Yes|No)', text, re.IGNORECASE)
        responses['underground_experience'] = underground_match.group(1) if underground_match else None
        
        # Employment Status
        # 31. Still with current company
        current_match = re.search(r'current company.*?resume.*?(Yes|No)', text, re.IGNORECASE)
        responses['still_with_current'] = current_match.group(1) if current_match else None
        
        # 32. Worked here before
        worked_before_match = re.search(r'worked for us before.*?(Yes|No)', text, re.IGNORECASE)
        responses['worked_here_before'] = worked_before_match.group(1) if worked_before_match else None
        
        # 33. Current employment status
        status_match = re.search(r'current employment status.*?(Employed|Unemployed|.*?)', text, re.IGNORECASE)
        responses['employment_status'] = status_match.group(1) if status_match else None
        
        # 34. Availability
        avail_match = re.search(r'available to start.*?(Within.*?month|Immediately|.*?)', text, re.IGNORECASE)
        responses['availability'] = avail_match.group(1) if avail_match else None
        
        # 35. Time off booked
        time_off_match = re.search(r'time off booked.*?(Yes|No)', text, re.IGNORECASE)
        responses['time_off_booked'] = time_off_match.group(1) if time_off_match else None
        
        # 36. Reason for looking
        reason_match = re.search(r'looking for.*?opportunity.*?(Work-Life Balance|.*?)', text, re.IGNORECASE)
        responses['reason_for_looking'] = reason_match.group(1) if reason_match else None
        
        # 37. Knows current employees
        knows_match = re.search(r'know anyone.*?working for us.*?(Yes|No)', text, re.IGNORECASE)
        responses['knows_employees'] = knows_match.group(1) if knows_match else None
        
        # 38. Contractor preference
        contractor_match = re.search(r'contractor.*?sub-contractor.*?(No.*?employee|Yes)', text, re.IGNORECASE)
        responses['contractor_preference'] = contractor_match.group(1) if contractor_match else None
        
        # Work Preferences
        # 39. Different mine sites
        sites_match = re.search(r'different mine sites.*?(Yes|No)', text, re.IGNORECASE)
        responses['willing_different_sites'] = sites_match.group(1) if sites_match else None
        
        # 40. Field work
        field_match = re.search(r'working in the field.*?(Yes|No)', text, re.IGNORECASE)
        responses['comfortable_field_work'] = field_match.group(1) if field_match else None
        
        # 41. Extended periods away
        away_match = re.search(r'away from home.*?extended.*?(Yes|No)', text, re.IGNORECASE)
        responses['commit_extended_periods'] = away_match.group(1) if away_match else None
        
        # 42. 3 weeks on/off rotation
        rotation3_match = re.search(r'3 weeks on/off.*?(Yes|No)', text, re.IGNORECASE)
        responses['willing_3week_rotation'] = rotation3_match.group(1) if rotation3_match else None
        
        # 43. Shared housing
        housing_match = re.search(r'shared housing.*?(Yes|No)', text, re.IGNORECASE)
        responses['comfortable_shared_housing'] = housing_match.group(1) if housing_match else None
        
        return responses
    
    def _create_summary(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of key points"""
        
        summary = {
            'key_strengths': [],
            'potential_concerns': [],
            'experience_highlights': [],
            'certifications': [],
            'work_preferences_summary': {}
        }
        
        # Certifications
        if responses.get('red_seal') == 'Yes':
            summary['certifications'].append('Red Seal Certified')
            summary['key_strengths'].append('Red Seal Certified')
        
        if responses.get('journeyman_license') == 'Yes':
            summary['certifications'].append('Journeyman Off-Road License')
            summary['key_strengths'].append('Journeyman Licensed')
        
        # Experience highlights
        if responses.get('service_truck_experience'):
            summary['experience_highlights'].append(f"Service truck: {responses['service_truck_experience']}")
        
        if responses.get('offroad_equipment_experience'):
            summary['experience_highlights'].append(f"Off-road equipment: {responses['offroad_equipment_experience']}")
        
        if responses.get('underground_experience') == 'Yes':
            summary['key_strengths'].append('Underground experience')
        
        # Technical skills
        if responses.get('pm_hydraulics_level') == 'Proficient':
            summary['key_strengths'].append('Proficient in hydraulics/PM')
        
        if responses.get('hydraulic_systems_level') == 'Intermediate':
            summary['key_strengths'].append('Intermediate hydraulic systems')
        
        # Potential concerns
        if responses.get('large_mining_equipment') == 'No Experience':
            summary['potential_concerns'].append('No large mining equipment experience')
        
        if responses.get('cat_et_sis_level') == 'Beginner':
            summary['potential_concerns'].append('Beginner level with CAT ET & SIS')
        
        if responses.get('underground_brands') == ['None of the above']:
            summary['potential_concerns'].append('No underground machinery brand experience')
        
        # Work preferences
        summary['work_preferences_summary'] = {
            'rotational_work': responses.get('willing_3week_rotation'),
            'field_work': responses.get('comfortable_field_work'),
            'different_sites': responses.get('willing_different_sites'),
            'availability': responses.get('availability'),
            'reason_for_looking': responses.get('reason_for_looking')
        }
        
        return summary


# Test the parser
if __name__ == "__main__":
    import fitz
    
    # Read the PDF
    doc = fitz.open('/mnt/c/Users/angel/Downloads/Recruiting - Dayforce.pdf')
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    
    # Parse with robust parser
    parser = RobustQuestionnaireParser()
    result = parser.parse_complete_questionnaire(text)
    
    print("=== ROBUST QUESTIONNAIRE PARSING ===")
    print(f"Candidate: {result['candidate_info']['name']}")
    print(f"Position: {result['candidate_info']['position']}")
    print(f"Date: {result['candidate_info']['date']}")
    print()
    
    print("=== KEY RESPONSES ===")
    responses = result['complete_responses']
    
    # Print non-None responses
    for key, value in responses.items():
        if value and value != 'Unknown':
            print(f"{key}: {value}")
    
    print()
    print("=== SUMMARY ===")
    summary = result['summary']
    print(f"Certifications: {summary['certifications']}")
    print(f"Key Strengths: {summary['key_strengths']}")
    print(f"Potential Concerns: {summary['potential_concerns']}")
    print(f"Experience Highlights: {summary['experience_highlights']}")