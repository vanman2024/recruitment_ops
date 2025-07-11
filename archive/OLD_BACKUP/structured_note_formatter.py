#!/usr/bin/env python3
"""
Structured Note Formatter - Extracts and formats candidate data per template
"""

import re
from typing import Dict, List, Any

class StructuredNoteFormatter:
    """Format candidate data into structured notes for hiring managers"""
    
    def __init__(self):
        self.sections = [
            "Personal and Contact Details",
            "Licenses, Certifications, and Related Qualifications",
            "Specialized Skills and Expertise",
            "Familiarity with Specific Tools, Brands, or Technologies",
            "Experience in Specific Roles or Environments",
            "Current Employment and Transition Reasons",
            "Additional Notes"
        ]
    
    def format_candidate_notes(self, form_data: Dict[str, Any], additional_notes: str = "") -> str:
        """Format candidate data into structured notes"""
        
        notes = []
        
        # 1. Personal and Contact Details
        personal = self._extract_personal_details(form_data)
        if personal:
            notes.append("**1. Personal and Contact Details**")
            for detail in personal:
                notes.append(f"• {detail}")
            notes.append("")
        
        # 2. Licenses, Certifications, and Related Qualifications
        certs = self._extract_certifications(form_data)
        if certs:
            notes.append("**2. Licenses, Certifications, and Related Qualifications**")
            for cert in certs:
                notes.append(f"• {cert}")
            notes.append("")
        
        # 3. Specialized Skills and Expertise
        skills = self._extract_skills(form_data)
        if skills:
            notes.append("**3. Specialized Skills and Expertise**")
            for skill in skills:
                notes.append(f"• {skill}")
            notes.append("")
        
        # 4. Familiarity with Specific Tools, Brands, or Technologies
        tools = self._extract_tools_and_brands(form_data)
        if tools:
            notes.append("**4. Familiarity with Specific Tools, Brands, or Technologies**")
            for tool in tools:
                notes.append(f"• {tool}")
            notes.append("")
        
        # 5. Experience in Specific Roles or Environments
        experience = self._extract_experience(form_data)
        if experience:
            notes.append("**5. Experience in Specific Roles or Environments**")
            for exp in experience:
                notes.append(f"• {exp}")
            notes.append("")
        
        # 6. Current Employment and Transition Reasons
        employment = self._extract_employment_status(form_data)
        if employment:
            notes.append("**6. Current Employment and Transition Reasons**")
            for emp in employment:
                notes.append(f"• {emp}")
            notes.append("")
        
        # 7. Additional Notes
        additional = self._extract_additional_notes(form_data, additional_notes)
        if additional:
            notes.append("**7. Additional Notes**")
            for note in additional:
                notes.append(f"• {note}")
        
        return "\n".join(notes)
    
    def _extract_personal_details(self, form_data: Dict) -> List[str]:
        """Extract personal and contact details"""
        details = []
        
        # Name
        if form_data.get('name'):
            details.append(f"Name: {form_data['name']}")
        
        # Email
        if form_data.get('email'):
            details.append(f"Email: {form_data['email']}")
        
        # Phone (without spaces or brackets)
        if form_data.get('phone'):
            phone = re.sub(r'[\s\(\)\-]', '', form_data['phone'])
            details.append(f"Phone: {phone}")
        
        # Location
        if form_data.get('location'):
            details.append(f"Location: {form_data['location']}")
        
        return details[:3]  # Max 3 items
    
    def _extract_certifications(self, form_data: Dict) -> List[str]:
        """Extract licenses and certifications"""
        certs = []
        
        # Red Seal
        if form_data.get('red_seal') == 'YES':
            certs.append("Red Seal Certified")
        
        # Other certifications
        cert_fields = ['whimis', 'tdg', 'first_aid', 'h2s', 'fall_arrest']
        for field in cert_fields:
            if form_data.get(field) == 'YES':
                cert_name = field.replace('_', ' ').title()
                certs.append(cert_name)
        
        # License types
        if form_data.get('license_class'):
            certs.append(f"Class {form_data['license_class']} License")
        
        return certs[:3]  # Max 3 items
    
    def _extract_skills(self, form_data: Dict) -> List[str]:
        """Extract specialized skills"""
        skills = []
        
        # Hydraulics
        if form_data.get('hydraulics_level'):
            skills.append(f"Hydraulic Systems: {form_data['hydraulics_level']} level")
        
        # Diagnostics
        if form_data.get('diagnostics') == 'YES':
            skills.append("Diagnostic and troubleshooting skills")
        
        # Years of experience
        if form_data.get('years_experience'):
            skills.append(f"{form_data['years_experience']} years heavy equipment experience")
        
        return skills[:3]
    
    def _extract_tools_and_brands(self, form_data: Dict) -> List[str]:
        """Extract tools, brands, and equipment"""
        tools = []
        
        # Equipment brands
        brands_list = []
        if form_data.get('equipment_brands'):
            brands_list = [b for b in form_data['equipment_brands'] if b != 'None of the above']
        
        if brands_list:
            tools.append(f"Equipment Brands: {', '.join(brands_list)}")
        elif form_data.get('equipment_brands') == ['None of the above']:
            tools.append("Equipment Brands: No specific brand experience reported")
        
        # Equipment types from written response
        if form_data.get('equipment_experience_written'):
            # Parse the written response for equipment types
            text = form_data['equipment_experience_written']
            # Extract equipment mentions
            equipment_found = []
            
            equipment_keywords = ['loader', 'excavator', 'truck', 'dozer', 'grader', 
                                'drill', 'shovel', 'hauler', 'crusher']
            
            for keyword in equipment_keywords:
                if keyword in text.lower():
                    equipment_found.append(keyword.title())
            
            if equipment_found:
                tools.append(f"Equipment Types: {', '.join(equipment_found)}")
        
        # Specific equipment experience
        if form_data.get('komatsu_experience') == 'YES':
            tools.append("Komatsu experience confirmed")
        
        return tools[:3]
    
    def _extract_experience(self, form_data: Dict) -> List[str]:
        """Extract role and environment experience"""
        experience = []
        
        # Industries
        if form_data.get('industries'):
            industries = [i for i in form_data['industries'] if i != 'Other']
            if industries:
                experience.append(f"Industries: {', '.join(industries)}")
        
        # Current role
        if form_data.get('current_role'):
            experience.append(f"Current Role: {form_data['current_role']}")
        
        # Specific environment experience
        if form_data.get('underground_experience') == 'YES':
            experience.append("Underground environment experience")
        
        return experience[:3]
    
    def _extract_employment_status(self, form_data: Dict) -> List[str]:
        """Extract employment and transition info"""
        employment = []
        
        # Current status
        if form_data.get('employment_status'):
            employment.append(f"Currently: {form_data['employment_status']}")
        
        # Current employer
        if form_data.get('current_employer'):
            employment.append(f"Current Employer: {form_data['current_employer']}")
        
        # Reason for looking
        if form_data.get('why_looking'):
            employment.append(f"Seeking new role for: {form_data['why_looking']}")
        
        # Availability
        if form_data.get('availability'):
            employment.append(f"Available to start: {form_data['availability']}")
        
        return employment[:3]
    
    def _extract_additional_notes(self, form_data: Dict, additional_notes: str) -> List[str]:
        """Extract additional relevant notes"""
        notes = []
        
        # Position applied for
        if form_data.get('position_applied'):
            notes.append(f"Applied for: {form_data['position_applied']}")
        
        # Any standout qualifications
        if form_data.get('years_experience'):
            years = form_data['years_experience']
            if isinstance(years, str) and '20+' in years or '15+' in years:
                notes.append("Extensive industry experience (15+ years)")
        
        # Add recruiter notes if provided
        if additional_notes:
            # Clean and add first sentence only
            clean_note = additional_notes.strip().split('.')[0]
            if clean_note:
                notes.append(clean_note)
        
        return notes[:3]


def format_from_questionnaire(questionnaire_data: Dict, recruiter_notes: str = "") -> str:
    """Main function to format questionnaire data"""
    
    formatter = StructuredNoteFormatter()
    
    # Transform questionnaire data into expected format
    form_data = {
        'name': questionnaire_data.get('candidate_name'),
        'email': questionnaire_data.get('email'),
        'phone': questionnaire_data.get('phone'),
        'location': questionnaire_data.get('location'),
        'red_seal': questionnaire_data.get('red_seal'),
        'industries': questionnaire_data.get('industries', []),
        'current_role': questionnaire_data.get('current_position'),
        'current_employer': questionnaire_data.get('current_company'),
        'employment_status': questionnaire_data.get('employment_status'),
        'why_looking': questionnaire_data.get('reason_for_looking'),
        'availability': questionnaire_data.get('availability'),
        'position_applied': questionnaire_data.get('position_interested'),
        'hydraulics_level': questionnaire_data.get('hydraulics_knowledge'),
        'equipment_brands': questionnaire_data.get('equipment_brands', []),
        'equipment_experience_written': questionnaire_data.get('equipment_written'),
        'years_experience': questionnaire_data.get('years_experience'),
        'underground_experience': questionnaire_data.get('underground_mechanic'),
        'komatsu_experience': questionnaire_data.get('komatsu_pc5000')
    }
    
    return formatter.format_candidate_notes(form_data, recruiter_notes)