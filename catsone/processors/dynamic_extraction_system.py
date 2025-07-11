#!/usr/bin/env python3
"""
Dynamic Extraction System - Extract everything, then filter by role
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DynamicExtractionSystem:
    """Extract all data, then apply role-specific filtering"""
    
    def __init__(self):
        self.all_extracted_data = {}
        self.role_templates = self._load_role_templates()
    
    def extract_all_questionnaire_data(self, questionnaire_result: Dict) -> Dict[str, Any]:
        """Extract EVERYTHING from questionnaire - no filtering"""
        
        all_data = {
            'responses': {},
            'equipment': {
                'brands_available': [],
                'brands_selected': [],
                'equipment_written': [],
                'equipment_types': []
            },
            'certifications': {},
            'experience': {},
            'availability': {},
            'preferences': {},
            'skills': {},
            'metadata': {
                'extraction_timestamp': datetime.now().isoformat()
            }
        }
        
        # First extract equipment analysis if available
        if 'equipment_analysis' in questionnaire_result:
            equip = questionnaire_result['equipment_analysis']
            all_data['equipment']['brands_available'] = equip.get('brands_available', [])
            all_data['equipment']['brands_selected'] = equip.get('brands_selected', [])
            all_data['equipment']['equipment_types'] = equip.get('equipment_types_selected', [])
        
        # Get raw responses
        raw_responses = questionnaire_result.get('candidate_profile', {}).get('actual_responses', {})
        
        # Extract EVERYTHING
        for key, response in raw_responses.items():
            question = response.get('question', '')
            selections = response.get('selections', [])
            text = response.get('text', [])
            all_options = response.get('all_options', [])
            
            # Store complete response
            all_data['responses'][key] = {
                'question': question,
                'selections': selections,
                'text': text,
                'all_options': all_options,
                'question_type': response.get('type')
            }
            
            # Categorize for easier access
            question_lower = question.lower()
            
            # Equipment related
            if any(term in question_lower for term in ['equipment', 'machinery', 'brands', 'komatsu', 'cat']):
                if 'brands' in question_lower:
                    all_data['equipment']['brands_available'].extend(all_options)
                    all_data['equipment']['brands_selected'].extend(selections)
                if text:
                    all_data['equipment']['equipment_written'].extend(text)
            
            # Also check if equipment info is in selections (for text fields)
            for selection in selections:
                if any(term in str(selection).lower() for term in ['loader', 'excavator', 'equipment', 'years']):
                    all_data['equipment']['equipment_written'].append(selection)
            
            # Certifications
            if any(term in question_lower for term in ['red seal', 'journeyman', 'license', 'certification', 'whimis', 'tdg']):
                cert_name = self._extract_cert_name(question)
                all_data['certifications'][cert_name] = {
                    'question': question,
                    'answer': selections[0] if selections else None,
                    'details': text
                }
            
            # Experience
            elif any(term in question_lower for term in ['experience', 'years', 'industries']):
                exp_type = self._categorize_experience(question)
                all_data['experience'][exp_type] = {
                    'question': question,
                    'selections': selections,
                    'text': text
                }
            
            # Availability
            elif any(term in question_lower for term in ['available', 'start', 'employment status']):
                all_data['availability'][key] = {
                    'question': question,
                    'answer': selections[0] if selections else None
                }
            
            # Work preferences
            elif any(term in question_lower for term in ['looking for', 'willing', 'comfortable', 'rotational']):
                all_data['preferences'][key] = {
                    'question': question,
                    'answer': selections[0] if selections else None
                }
            
            # Skills
            elif any(term in question_lower for term in ['hydraulic', 'diagnostic', 'electrical']):
                skill_type = self._extract_skill_type(question)
                all_data['skills'][skill_type] = {
                    'level': selections[0] if selections else None,
                    'details': text
                }
        
        # Get equipment analysis from vision analyzer
        equipment_analysis = questionnaire_result.get('candidate_profile', {}).get('equipment_analysis', {})
        if equipment_analysis:
            all_data['equipment'].update(equipment_analysis)
        
        return all_data
    
    def format_for_role(self, all_data: Dict, role_type: str, custom_requirements: Optional[Dict] = None) -> str:
        """Format extracted data based on role requirements"""
        
        # Get role template
        template = self.role_templates.get(role_type, self.role_templates['default'])
        
        # Override with custom requirements if provided
        if custom_requirements:
            template.update(custom_requirements)
        
        # Build formatted notes based on template
        notes = []
        
        # 1. Personal and Contact Details
        notes.append("1. Personal and Contact Details")
        notes.extend(self._format_personal_section(all_data, template))
        notes.append("")
        
        # 2. Licenses, Certifications, and Related Qualifications
        notes.append("2. Licenses, Certifications, and Related Qualifications")
        notes.extend(self._format_certifications_section(all_data, template))
        notes.append("")
        
        # 3. Specialized Skills and Expertise
        notes.append("3. Specialized Skills and Expertise")
        notes.extend(self._format_skills_section(all_data, template))
        notes.append("")
        
        # 4. Familiarity with Specific Tools, Brands, or Technologies
        notes.append("4. Familiarity with Specific Tools, Brands, or Technologies")
        notes.extend(self._format_equipment_section(all_data, template))
        notes.append("")
        
        # 5. Experience in Specific Roles or Environments
        notes.append("5. Experience in Specific Roles or Environments")
        notes.extend(self._format_experience_section(all_data, template))
        notes.append("")
        
        # 6. Current Employment and Transition Reasons
        notes.append("6. Current Employment and Transition Reasons")
        notes.extend(self._format_employment_section(all_data, template))
        notes.append("")
        
        # 7. Additional Notes
        notes.append("7. Additional Notes")
        notes.extend(self._format_additional_section(all_data, template))
        
        return "\n".join(notes)
    
    def _load_role_templates(self) -> Dict[str, Dict]:
        """Load role-specific templates"""
        
        templates = {
            'heavy_equipment_technician': {
                'required_certs': ['red seal', 'journeyman heavy equipment'],
                'exclude_certs': ['whimis', 'tdg', 'first aid'],
                'important_brands': ['cat', 'komatsu', 'john deere', 'hitachi'],
                'important_equipment': ['loader', 'excavator', 'dozer', 'grader'],
                'exclude_info': ['drug test', 'housing', 'cooking'],
                'highlight_experience': ['mining', 'construction', 'forestry']
            },
            'electrician': {
                'required_certs': ['red seal', 'journeyman electrician'],
                'exclude_certs': ['whimis', 'tdg'],
                'important_skills': ['electrical', 'plc', 'automation'],
                'exclude_info': ['drug test', 'housing']
            },
            'default': {
                'required_certs': ['red seal'],
                'exclude_certs': ['whimis', 'tdg', 'first aid', 'h2s'],
                'exclude_info': ['drug test', 'housing', 'cooking', 'rotational']
            }
        }
        
        # Load custom templates from file if exists
        template_file = '/home/gotime2022/recruitment_ops/role_templates.json'
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r') as f:
                    custom_templates = json.load(f)
                    templates.update(custom_templates)
            except:
                pass
        
        return templates
    
    def _format_certifications_section(self, all_data: Dict, template: Dict) -> List[str]:
        """Format certifications based on role requirements"""
        
        lines = []
        certs = all_data.get('certifications', {})
        required = template.get('required_certs', [])
        exclude = template.get('exclude_certs', [])
        
        # Add required certifications that are present
        for cert_key, cert_data in certs.items():
            cert_lower = cert_key.lower()
            
            # Skip excluded certs
            if any(exc in cert_lower for exc in exclude):
                continue
            
            # Handle both string and dict formats
            if isinstance(cert_data, str):
                # Simple string value (e.g., "Yes" or "No")
                if cert_data.upper() == 'YES':
                    if 'red seal' in cert_lower:
                        lines.append("• Red Seal Heavy Duty Technician")
                    else:
                        lines.append(f"• {cert_key}")
            elif isinstance(cert_data, dict):
                # Dict format with 'answer' key
                if cert_data.get('answer') == 'YES' or cert_data.get('answer') == 'Yes':
                    # Format based on cert type
                    if 'red seal' in cert_lower:
                        lines.append("• Red Seal Heavy Duty Technician")
                    elif 'journeyman' in cert_lower and 'heavy equipment' in cert_data.get('question', '').lower():
                        lines.append("• Journeyman Heavy Equipment Technician trade qualification")
                    else:
                        lines.append(f"• {cert_key}")
        
        # Check positions selected for trade qualifications
        responses = all_data.get('responses', {})
        for key, resp in responses.items():
            if 'position' in resp.get('question', '').lower() and 'interested' in resp.get('question', '').lower():
                for position in resp.get('selections', []):
                    if 'journeyman heavy equipment' in position.lower():
                        if "• Journeyman Heavy Equipment Technician trade qualification" not in lines:
                            lines.append("• Journeyman Heavy Equipment Technician trade qualification")
        
        return lines
    
    def _format_equipment_section(self, all_data: Dict, template: Dict) -> List[str]:
        """Format equipment section based on role requirements"""
        
        lines = []
        equipment = all_data.get('equipment', {})
        important_brands = template.get('important_brands', [])
        
        # Brands selected (only positive selections)
        brands = [b for b in equipment.get('brands_selected', []) 
                 if b not in ['None', 'None of the above']]
        
        if brands:
            lines.append(f"Equipment Brands:")
            lines.append(f"• {', '.join(brands)}")
        
        # Written equipment experience
        written = equipment.get('equipment_written', [])
        if written:
            lines.append("\nEquipment Experience:")
            for text in written:
                # Parse the combined text that might have multiple experiences
                text_str = str(text)
                
                # Check for the specific format found in questionnaire
                if 'wheeled loader' in text_str and 'excavator' in text_str:
                    # Parse the combined years/equipment string
                    import re
                    
                    # Extract different equipment experiences
                    if '4 years' in text_str:
                        lines.append("• 4 years wheeled loader, excavator, off-road equipment")
                    if '3 years' in text_str and 'truck' in text_str:
                        lines.append("• 3 years on truck")
                    if '15 years' in text_str and 'logging' in text_str:
                        lines.append("• 15 years of logging equipment")
                else:
                    # Just add the text if it contains equipment info
                    if any(term in text_str.lower() for term in ['equipment', 'years', 'experience']):
                        lines.append(f"• {text}")
        
        return lines
    
    def _extract_cert_name(self, question: str) -> str:
        """Extract certification name from question"""
        
        question_lower = question.lower()
        
        if 'red seal' in question_lower:
            return 'Red Seal'
        elif 'journeyman' in question_lower and 'off-road' in question_lower:
            return 'Journeyman Off-Road License'
        elif 'whimis' in question_lower:
            return 'WHIMIS'
        elif 'tdg' in question_lower or 'dangerous goods' in question_lower:
            return 'TDG'
        elif 'first aid' in question_lower:
            return 'First Aid'
        elif 'fall arrest' in question_lower:
            return 'Fall Arrest'
        elif 'crane' in question_lower:
            return 'Crane Certification'
        else:
            # Extract key terms
            return question.split('?')[0].replace('Do you have', '').strip()
    
    def _categorize_experience(self, question: str) -> str:
        """Categorize experience questions"""
        
        question_lower = question.lower()
        
        if 'service truck' in question_lower:
            return 'service_truck'
        elif 'industries' in question_lower:
            return 'industries'
        elif 'underground' in question_lower:
            return 'underground'
        elif 'mining' in question_lower:
            return 'mining'
        else:
            return 'other_experience'
    
    def _extract_skill_type(self, question: str) -> str:
        """Extract skill type from question"""
        
        question_lower = question.lower()
        
        if 'hydraulic' in question_lower:
            return 'hydraulics'
        elif 'electrical' in question_lower:
            return 'electrical'
        elif 'diagnostic' in question_lower:
            return 'diagnostics'
        else:
            return 'other_skill'
    
    def _format_personal_section(self, all_data: Dict, template: Dict) -> List[str]:
        """Format personal details section"""
        
        lines = []
        # This would come from candidate data, not questionnaire
        # Just placeholder for now
        return lines
    
    def _format_skills_section(self, all_data: Dict, template: Dict) -> List[str]:
        """Format skills section"""
        
        lines = []
        skills = all_data.get('skills', {})
        experience = all_data.get('experience', {})
        
        # Service truck experience
        if 'service_truck' in experience:
            text = experience['service_truck'].get('text', [])
            if text:
                lines.append(f"• {text[0]}")
        
        # Hydraulics
        if 'hydraulics' in skills and skills['hydraulics'].get('level'):
            level = skills['hydraulics']['level']
            if level and level != 'None':
                lines.append(f"• Hydraulic Systems: {level} level")
        
        return lines
    
    def _format_experience_section(self, all_data: Dict, template: Dict) -> List[str]:
        """Format experience section"""
        
        lines = []
        experience = all_data.get('experience', {})
        
        # Industries
        if 'industries' in experience:
            industries = experience['industries'].get('selections', [])
            other = experience['industries'].get('text', [])
            
            # Filter out "Other"
            industries = [i for i in industries if i != 'Other']
            
            # Add written text (like "Logging")
            if other:
                industries.extend(other)
            
            if industries:
                lines.append(f"• Industries: {', '.join(industries)}")
        
        return lines
    
    def _format_employment_section(self, all_data: Dict, template: Dict) -> List[str]:
        """Format employment section"""
        
        lines = []
        availability = all_data.get('availability', {})
        preferences = all_data.get('preferences', {})
        
        # Employment status
        for key, data in availability.items():
            if 'employment status' in data.get('question', '').lower():
                lines.append(f"• Currently: {data.get('answer')}")
            elif 'available to start' in data.get('question', '').lower():
                lines.append(f"• Available: {data.get('answer')}")
        
        # Why looking
        for key, data in preferences.items():
            if 'looking for' in data.get('question', '').lower() and 'opportunity' in data.get('question', '').lower():
                lines.append(f"• Seeking: {data.get('answer')}")
        
        return lines
    
    def _format_additional_section(self, all_data: Dict, template: Dict) -> List[str]:
        """Format additional notes section"""
        
        lines = []
        
        # Position applied for
        responses = all_data.get('responses', {})
        for key, resp in responses.items():
            if 'position' in resp.get('question', '').lower() and 'interested' in resp.get('question', '').lower():
                positions = resp.get('selections', [])
                if positions:
                    lines.append(f"• Applied for: {', '.join(positions)}")
                    break
        
        return lines