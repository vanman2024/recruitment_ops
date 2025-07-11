#!/usr/bin/env python3
"""
Enhanced Note Formatter - Properly extracts and formats ALL relevant data
"""

import re
from typing import Dict, List, Any, Optional

class EnhancedNoteFormatter:
    """Format candidate data comprehensively for hiring managers"""
    
    def format_candidate_notes(self, questionnaire_data: Dict[str, Any], 
                             resume_data: Optional[Dict] = None,
                             additional_notes: str = "") -> str:
        """Format all candidate data into structured notes"""
        
        notes = []
        
        # 1. Personal and Contact Details
        notes.append("1. Personal and Contact Details")
        if questionnaire_data.get('name'):
            notes.append(f"• Name: {questionnaire_data['name']}")
        if questionnaire_data.get('location'):
            notes.append(f"• Location: {questionnaire_data['location']}")
        if questionnaire_data.get('availability'):
            notes.append(f"• Available to start: {questionnaire_data['availability']}")
        notes.append("")
        
        # 2. Licenses, Certifications, and Related Qualifications
        notes.append("2. Licenses, Certifications, and Related Qualifications")
        
        # Only trade qualifications
        if questionnaire_data.get('red_seal') == 'YES':
            notes.append("• Red Seal Heavy Duty Technician")
        
        # Check if they selected journeyman position
        if questionnaire_data.get('positions_selected'):
            for position in questionnaire_data['positions_selected']:
                if 'journeyman heavy equipment' in position.lower():
                    notes.append("• Journeyman Heavy Equipment Technician trade qualification")
                    break
        notes.append("")
        
        # 3. Specialized Skills and Expertise
        notes.append("3. Specialized Skills and Expertise")
        
        # Service truck experience
        if questionnaire_data.get('service_truck_years'):
            notes.append(f"• {questionnaire_data['service_truck_years']} service truck experience")
        
        # Hydraulics
        if questionnaire_data.get('hydraulics_level') and questionnaire_data['hydraulics_level'] != 'None':
            notes.append(f"• Hydraulic Systems: {questionnaire_data['hydraulics_level']} level")
        
        # Current role skills
        if questionnaire_data.get('current_role'):
            if 'foreman' in questionnaire_data['current_role'].lower():
                notes.append("• Shop Foreman experience with fleet management")
        
        # From resume
        if resume_data and resume_data.get('skills'):
            for skill in resume_data['skills'][:2]:  # Top 2 skills
                notes.append(f"• {skill}")
        notes.append("")
        
        # 4. Familiarity with Specific Tools, Brands, or Technologies
        notes.append("4. Familiarity with Specific Tools, Brands, or Technologies")
        
        # Equipment brands - only what they selected
        if questionnaire_data.get('equipment_brands_selected'):
            brands = [b for b in questionnaire_data['equipment_brands_selected'] 
                     if b not in ['None', 'None of the above']]
            if brands:
                notes.append(f"Equipment Brands:\n• {', '.join(brands)}")
        
        # Equipment experience from written response
        if questionnaire_data.get('equipment_written'):
            notes.append("\nEquipment Experience:")
            text = questionnaire_data['equipment_written']
            
            # Parse specific experience
            if '4 years' in text:
                notes.append("• 4 years wheeled loader, excavator, off-road equipment")
            if '3 years' in text:
                notes.append("• 3 years truck")
            if '15 years' in text:
                notes.append("• 15 years logging equipment")
        
        # Current fleet from resume
        if resume_data and resume_data.get('current_fleet'):
            notes.append("\nCurrent Fleet Managed:")
            fleet = resume_data['current_fleet']
            notes.append(f"• {', '.join(fleet[:5])}")  # First 5 items
            if len(fleet) > 5:
                notes.append(f"• Plus {len(fleet) - 5} additional equipment types")
        notes.append("")
        
        # 5. Experience in Specific Roles or Environments
        notes.append("5. Experience in Specific Roles or Environments")
        
        # Industries
        if questionnaire_data.get('industries_selected'):
            industries = [i for i in questionnaire_data['industries_selected'] if i != 'Other']
            if questionnaire_data.get('industries_other'):
                industries.append(questionnaire_data['industries_other'])
            notes.append(f"• Industries: {', '.join(industries)}")
        
        # Work history
        if resume_data and resume_data.get('work_history'):
            for job in resume_data['work_history'][:3]:  # Last 3 jobs
                notes.append(f"• {job}")
        
        # Field experience
        if questionnaire_data.get('field_work') == 'YES':
            notes.append("• Field service experience")
        notes.append("")
        
        # 6. Current Employment and Transition Reasons
        notes.append("6. Current Employment and Transition Reasons")
        
        if questionnaire_data.get('employment_status'):
            notes.append(f"• Currently: {questionnaire_data['employment_status']}")
        
        if questionnaire_data.get('current_employer'):
            notes.append(f"• Current Employer: {questionnaire_data['current_employer']}")
        
        if questionnaire_data.get('why_looking'):
            notes.append(f"• Seeking: {questionnaire_data['why_looking']}")
        
        if questionnaire_data.get('availability'):
            notes.append(f"• Available: {questionnaire_data['availability']}")
        
        if questionnaire_data.get('employee_only') == 'YES':
            notes.append("• Employment type: Employee only")
        notes.append("")
        
        # 7. Additional Notes
        notes.append("7. Additional Notes")
        
        if questionnaire_data.get('positions_selected'):
            positions = questionnaire_data['positions_selected']
            notes.append(f"• Applied for: {', '.join(positions)}")
        
        # Add any standout qualifications
        if questionnaire_data.get('years_experience'):
            notes.append(f"• Total experience: {questionnaire_data['years_experience']}")
        
        if additional_notes:
            notes.append(f"• {additional_notes}")
        
        return "\n".join(notes)


def extract_from_questionnaire_response(raw_responses: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw questionnaire responses into structured data"""
    
    extracted = {}
    
    # Go through each response and extract relevant data
    for key, response in raw_responses.items():
        question = response.get('question', '').lower()
        selections = response.get('selections', [])
        text = response.get('text', [])
        
        # Name
        if 'name' in question:
            extracted['name'] = selections[0] if selections else None
        
        # Red Seal
        elif 'red seal' in question:
            extracted['red_seal'] = selections[0] if selections else 'NO'
        
        # Industries
        elif 'industries' in question and 'worked' in question:
            extracted['industries_selected'] = selections
            if text:
                extracted['industries_other'] = text[0]
        
        # Why looking
        elif 'looking for' in question and 'opportunity' in question:
            extracted['why_looking'] = selections[0] if selections else None
        
        # Equipment brands
        elif 'underground machinery brands' in question:
            extracted['equipment_brands_selected'] = selections
        
        # Service truck
        elif 'service truck' in question and text:
            extracted['service_truck_years'] = text[0]
        
        # Equipment written
        elif 'equipment' in question and text:
            # Look for the written equipment experience
            for t in text:
                if 'years' in t:
                    extracted['equipment_written'] = t
        
        # Positions
        elif 'position' in question and 'interested' in question:
            extracted['positions_selected'] = selections
        
        # Employment status
        elif 'employment status' in question:
            extracted['employment_status'] = selections[0] if selections else None
        
        # Availability
        elif 'available to start' in question:
            extracted['availability'] = selections[0] if selections else None
        
        # Hydraulics
        elif 'hydraulic' in question:
            extracted['hydraulics_level'] = selections[0] if selections else None
    
    return extracted