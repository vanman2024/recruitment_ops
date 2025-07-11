#!/usr/bin/env python3
"""
Job Requirements Extractor - Pulls requirements from job description AND notes
"""

import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class JobRequirementsExtractor:
    """Extract and parse job requirements from CATS job postings"""
    
    def extract_job_requirements(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract requirements from job description and notes"""
        
        requirements = {
            'role_type': self._identify_role_type(job_data),
            'required_certifications': [],
            'preferred_certifications': [],
            'required_brands': [],
            'preferred_brands': [],
            'required_equipment': [],
            'preferred_equipment': [],
            'required_experience': [],
            'key_skills': [],
            'exclude_from_notes': [],
            'highlight_in_notes': [],
            'custom_filters': {},
            'source': {
                'job_id': job_data.get('id'),
                'job_title': job_data.get('title'),
                'has_notes': bool(job_data.get('notes'))
            }
        }
        
        # Extract from main job description
        description = job_data.get('description', '')
        if description:
            self._parse_description(description, requirements)
        
        # Extract from notes section (YOUR custom requirements)
        notes = job_data.get('notes', '')
        if notes:
            self._parse_notes_section(notes, requirements)
        
        # Extract from requirements field if exists
        requirements_text = job_data.get('requirements', '')
        if requirements_text:
            self._parse_requirements_text(requirements_text, requirements)
        
        return requirements
    
    def _parse_notes_section(self, notes: str, requirements: Dict):
        """Parse custom notes section for specific extraction rules"""
        
        # Look for specific patterns in notes
        lines = notes.split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Section headers you might use
            if line.startswith('REQUIRED:'):
                current_section = 'required'
            elif line.startswith('PREFERRED:'):
                current_section = 'preferred'
            elif line.startswith('EXCLUDE:'):
                current_section = 'exclude'
            elif line.startswith('HIGHLIGHT:'):
                current_section = 'highlight'
            elif line.startswith('BRANDS:'):
                current_section = 'brands'
            elif line.startswith('EQUIPMENT:'):
                current_section = 'equipment'
            elif line.startswith('CERTIFICATIONS:'):
                current_section = 'certifications'
            elif line.startswith('FILTER:'):
                current_section = 'filter'
            else:
                # Process line based on current section
                if current_section == 'required' and ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    if 'cert' in key:
                        requirements['required_certifications'].append(value.strip())
                    elif 'brand' in key:
                        requirements['required_brands'].extend(self._extract_list(value))
                    elif 'equipment' in key:
                        requirements['required_equipment'].extend(self._extract_list(value))
                
                elif current_section == 'exclude':
                    requirements['exclude_from_notes'].append(line)
                
                elif current_section == 'highlight':
                    requirements['highlight_in_notes'].append(line)
                
                elif current_section == 'filter':
                    # Custom filter rules
                    if ':' in line:
                        filter_name, filter_value = line.split(':', 1)
                        requirements['custom_filters'][filter_name.strip()] = filter_value.strip()
        
        # Also look for inline markers
        if 'SHOW:' in notes:
            # Extract what to show
            show_matches = re.findall(r'SHOW:\s*([^\n]+)', notes)
            for match in show_matches:
                requirements['highlight_in_notes'].extend(self._extract_list(match))
        
        if 'HIDE:' in notes:
            # Extract what to hide
            hide_matches = re.findall(r'HIDE:\s*([^\n]+)', notes)
            for match in hide_matches:
                requirements['exclude_from_notes'].extend(self._extract_list(match))
    
    def _parse_description(self, description: str, requirements: Dict):
        """Parse standard job description for requirements"""
        
        description_lower = description.lower()
        
        # Extract certifications
        cert_patterns = [
            r'red seal[^.]*required',
            r'journeyman[^.]*required',
            r'must have[^.]*red seal',
            r'must have[^.]*journeyman'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, description_lower)
            for match in matches:
                if 'red seal' in match:
                    requirements['required_certifications'].append('Red Seal')
                if 'journeyman' in match:
                    # Extract specific journeyman type
                    if 'heavy equipment' in match:
                        requirements['required_certifications'].append('Journeyman Heavy Equipment Technician')
                    elif 'electrician' in match:
                        requirements['required_certifications'].append('Journeyman Electrician')
        
        # Extract equipment brands
        brand_keywords = ['cat', 'caterpillar', 'komatsu', 'john deere', 'hitachi', 
                         'volvo', 'liebherr', 'sandvik', 'epiroc']
        
        for brand in brand_keywords:
            if brand in description_lower:
                if 'required' in description_lower[max(0, description_lower.find(brand)-50):description_lower.find(brand)+50]:
                    requirements['required_brands'].append(brand.title())
                else:
                    requirements['preferred_brands'].append(brand.title())
        
        # Extract experience requirements
        exp_patterns = [
            r'(\d+)\+?\s*years[^.]*experience',
            r'minimum[^.]*(\d+)\s*years',
            r'at least[^.]*(\d+)\s*years'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, description_lower)
            for match in matches:
                requirements['required_experience'].append(f"{match} years")
    
    def _parse_requirements_text(self, req_text: str, requirements: Dict):
        """Parse specific requirements field"""
        
        lines = req_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                line = line[1:].strip()
                
                # Categorize requirement
                if any(cert in line.lower() for cert in ['certification', 'license', 'red seal', 'journeyman']):
                    if 'preferred' not in line.lower():
                        requirements['required_certifications'].append(line)
                    else:
                        requirements['preferred_certifications'].append(line)
                
                elif any(brand in line.lower() for brand in ['cat', 'komatsu', 'deere', 'hitachi']):
                    requirements['preferred_brands'].append(line)
                
                elif 'experience' in line.lower():
                    requirements['required_experience'].append(line)
    
    def _identify_role_type(self, job_data: Dict) -> str:
        """Identify the role type from job title"""
        
        title = job_data.get('title', '').lower()
        
        if 'heavy equipment' in title and 'technician' in title:
            return 'heavy_equipment_technician'
        elif 'electrician' in title:
            return 'electrician'
        elif 'welder' in title:
            return 'journeyman_welder'
        elif 'millwright' in title:
            return 'millwright'
        else:
            return 'default'
    
    def _extract_list(self, text: str) -> List[str]:
        """Extract comma-separated list from text"""
        
        items = []
        if ',' in text:
            items = [item.strip() for item in text.split(',')]
        else:
            items = [text.strip()]
        
        return [item for item in items if item]


def format_extraction_template(job_requirements: Dict) -> str:
    """Generate extraction template based on job requirements"""
    
    template = f"""
EXTRACTION TEMPLATE FOR: {job_requirements['source']['job_title']}
================================================

REQUIRED CERTIFICATIONS TO SHOW:
{chr(10).join('• ' + cert for cert in job_requirements['required_certifications'])}

EQUIPMENT BRANDS TO HIGHLIGHT:
Required: {', '.join(job_requirements['required_brands'])}
Preferred: {', '.join(job_requirements['preferred_brands'])}

EXCLUDE FROM NOTES:
{chr(10).join('• ' + item for item in job_requirements['exclude_from_notes'])}

CUSTOM FILTERS:
{chr(10).join(f'• {k}: {v}' for k, v in job_requirements['custom_filters'].items())}
"""
    
    return template