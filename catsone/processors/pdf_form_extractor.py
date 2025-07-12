#!/usr/bin/env python3
"""
Direct PDF form field extraction for accurate questionnaire data retrieval
"""

import os
import logging
from typing import Dict, Any, Optional, List
import PyPDF2
from PyPDF2 import PdfReader
from PyPDF2.generic import NameObject, TextStringObject
import json

logger = logging.getLogger(__name__)

class PDFFormExtractor:
    """Extract form field data directly from PDF files"""
    
    def __init__(self):
        self.field_mappings = {
            # Common form field names to standardized keys
            'red_seal': ['red seal', 'redseal', 'red_seal_status', 'has_red_seal'],
            'trade_licenses': ['trade_license', 'licenses', 'trade licenses', 'certifications'],
            'years_experience': ['years', 'experience', 'years_of_experience', 'exp_years'],
            'willing_to_travel': ['travel', 'willing_travel', 'can_travel', 'travel_willing'],
            'available_start': ['start_date', 'available_date', 'availability', 'can_start'],
            'preferred_location': ['location', 'preferred_loc', 'work_location', 'city'],
            'hourly_rate': ['rate', 'hourly', 'wage', 'salary', 'pay_rate'],
            'overtime_willing': ['overtime', 'ot', 'overtime_willing', 'work_overtime'],
            'safety_tickets': ['safety', 'tickets', 'safety_tickets', 'certifications'],
            'union_member': ['union', 'union_member', 'union_status', 'is_union'],
        }
    
    def extract_form_data(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all form field data from a PDF"""
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                
                # Check if PDF has form fields
                if '/AcroForm' not in reader.trailer['/Root']:
                    logger.info(f"No form fields found in {pdf_path}")
                    return {'has_form_fields': False}
                
                # Get form fields
                form_fields = reader.get_form_text_fields()
                
                if not form_fields:
                    logger.info(f"No filled form fields in {pdf_path}")
                    return {'has_form_fields': True, 'fields': {}}
                
                # Extract and normalize field data
                extracted_data = {
                    'has_form_fields': True,
                    'raw_fields': form_fields,
                    'normalized_fields': self._normalize_fields(form_fields),
                    'questionnaire_data': self._extract_questionnaire_data(form_fields)
                }
                
                logger.info(f"Extracted {len(form_fields)} form fields from {pdf_path}")
                return extracted_data
                
        except Exception as e:
            logger.error(f"Error extracting form data from {pdf_path}: {e}")
            return {'has_form_fields': False, 'error': str(e)}
    
    def extract_all_fields(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all form fields including checkboxes and radio buttons"""
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                
                if '/AcroForm' not in reader.trailer['/Root']:
                    return {'has_form_fields': False}
                
                fields = reader.get_fields()
                extracted = {
                    'has_form_fields': True,
                    'text_fields': {},
                    'checkboxes': {},
                    'radio_buttons': {},
                    'other_fields': {}
                }
                
                for field_name, field_obj in fields.items():
                    field_type = field_obj.get('/FT')
                    field_value = field_obj.get('/V')
                    
                    # Handle different field types
                    if field_type == '/Tx':  # Text field
                        extracted['text_fields'][field_name] = self._get_field_value(field_obj)
                    
                    elif field_type == '/Btn':  # Button (checkbox or radio)
                        # Check if it's a checkbox or radio button
                        field_flags = field_obj.get('/Ff', 0)
                        
                        if field_flags & 65536:  # Radio button
                            extracted['radio_buttons'][field_name] = {
                                'selected': self._get_radio_value(field_obj),
                                'options': self._get_radio_options(field_obj)
                            }
                        else:  # Checkbox
                            extracted['checkboxes'][field_name] = self._is_checkbox_checked(field_obj)
                    
                    else:  # Other field types
                        extracted['other_fields'][field_name] = {
                            'type': str(field_type),
                            'value': str(field_value) if field_value else None
                        }
                
                # Add normalized questionnaire data
                extracted['questionnaire_data'] = self._process_extracted_fields(extracted)
                
                return extracted
                
        except Exception as e:
            logger.error(f"Error extracting all fields: {e}")
            return {'has_form_fields': False, 'error': str(e)}
    
    def _normalize_fields(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Normalize field names to standard keys"""
        
        normalized = {}
        
        for field_name, value in fields.items():
            # Clean field name
            clean_name = field_name.lower().strip().replace('_', ' ')
            
            # Try to match to known field types
            matched = False
            for standard_key, variations in self.field_mappings.items():
                for variation in variations:
                    if variation in clean_name:
                        normalized[standard_key] = value
                        matched = True
                        break
                if matched:
                    break
            
            # If no match, use cleaned original name
            if not matched:
                normalized[clean_name] = value
        
        return normalized
    
    def _extract_questionnaire_data(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Extract specific questionnaire data from form fields"""
        
        data = {}
        normalized = self._normalize_fields(fields)
        
        # Extract Red Seal status
        if 'red_seal' in normalized:
            value = normalized['red_seal'].lower().strip()
            data['red_seal_status'] = 'Yes' if value in ['yes', 'y', 'true', '1', 'x'] else 'No'
        
        # Extract trade licenses
        if 'trade_licenses' in normalized:
            licenses_text = normalized['trade_licenses']
            data['trade_licenses'] = self._parse_licenses(licenses_text)
        
        # Extract years of experience
        if 'years_experience' in normalized:
            data['years_experience'] = self._parse_years(normalized['years_experience'])
        
        # Extract travel willingness
        if 'willing_to_travel' in normalized:
            value = normalized['willing_to_travel'].lower().strip()
            data['willing_to_travel'] = value in ['yes', 'y', 'true', '1', 'x']
        
        # Extract other fields
        for key in ['available_start', 'preferred_location', 'hourly_rate', 
                    'overtime_willing', 'safety_tickets', 'union_member']:
            if key in normalized:
                data[key] = normalized[key]
        
        return data
    
    def _get_field_value(self, field_obj: Dict) -> Optional[str]:
        """Get the value of a text field"""
        
        value = field_obj.get('/V')
        if value:
            if isinstance(value, TextStringObject):
                return str(value)
            elif isinstance(value, bytes):
                return value.decode('utf-8', errors='ignore')
            else:
                return str(value)
        return None
    
    def _is_checkbox_checked(self, field_obj: Dict) -> bool:
        """Check if a checkbox is checked"""
        
        value = field_obj.get('/V')
        if value:
            if isinstance(value, NameObject):
                # Common values for checked: /Yes, /On, /1
                return str(value) in ['/Yes', '/On', '/1']
            elif isinstance(value, (str, bytes)):
                return str(value).lower() in ['yes', 'on', '1', 'true', 'x']
        
        # Check appearance state
        as_value = field_obj.get('/AS')
        if as_value and isinstance(as_value, NameObject):
            return str(as_value) in ['/Yes', '/On', '/1']
        
        return False
    
    def _get_radio_value(self, field_obj: Dict) -> Optional[str]:
        """Get the selected value of a radio button group"""
        
        value = field_obj.get('/V')
        if value:
            if isinstance(value, NameObject):
                return str(value).lstrip('/')
            else:
                return str(value)
        return None
    
    def _get_radio_options(self, field_obj: Dict) -> List[str]:
        """Get all options for a radio button group"""
        
        options = []
        
        # Check for /Opt array (option labels)
        opt = field_obj.get('/Opt')
        if opt:
            for option in opt:
                if isinstance(option, list) and len(option) >= 2:
                    options.append(str(option[1]))
                else:
                    options.append(str(option))
        
        # Check Kids for radio button options
        kids = field_obj.get('/Kids', [])
        for kid in kids:
            if isinstance(kid, dict):
                # Get the export value
                export_value = kid.get('/AS')
                if export_value:
                    options.append(str(export_value).lstrip('/'))
        
        return options
    
    def _process_extracted_fields(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """Process extracted fields into questionnaire data"""
        
        data = {}
        
        # Process text fields
        if 'text_fields' in extracted:
            normalized = self._normalize_fields(extracted['text_fields'])
            data.update(self._extract_questionnaire_data(extracted['text_fields']))
        
        # Process checkboxes
        if 'checkboxes' in extracted:
            for field_name, is_checked in extracted['checkboxes'].items():
                clean_name = field_name.lower().strip()
                
                # Check for Red Seal checkbox
                if 'red' in clean_name and 'seal' in clean_name:
                    data['red_seal_status'] = 'Yes' if is_checked else 'No'
                
                # Check for travel willingness
                elif 'travel' in clean_name:
                    data['willing_to_travel'] = is_checked
                
                # Check for overtime
                elif 'overtime' in clean_name:
                    data['overtime_willing'] = is_checked
                
                # Check for union
                elif 'union' in clean_name:
                    data['union_member'] = is_checked
        
        # Process radio buttons
        if 'radio_buttons' in extracted:
            for field_name, radio_data in extracted['radio_buttons'].items():
                clean_name = field_name.lower().strip()
                selected = radio_data.get('selected')
                
                if selected:
                    # Map to appropriate field
                    if 'red' in clean_name and 'seal' in clean_name:
                        data['red_seal_status'] = selected
                    elif 'experience' in clean_name:
                        data['years_experience'] = selected
                    else:
                        data[clean_name] = selected
        
        return data
    
    def _parse_licenses(self, licenses_text: str) -> List[str]:
        """Parse trade licenses from text"""
        
        # Common separators
        separators = [',', ';', '\n', '•', '-']
        
        licenses = []
        current_text = licenses_text
        
        # Split by separators
        for sep in separators:
            if sep in current_text:
                parts = current_text.split(sep)
                for part in parts:
                    clean_part = part.strip()
                    if clean_part and len(clean_part) > 2:
                        licenses.append(clean_part)
                return licenses
        
        # If no separator found, return as single license
        if licenses_text.strip():
            licenses.append(licenses_text.strip())
        
        return licenses
    
    def _parse_years(self, years_text: str) -> Optional[int]:
        """Parse years of experience from text"""
        
        import re
        
        # Look for numbers
        numbers = re.findall(r'\d+', years_text)
        if numbers:
            return int(numbers[0])
        
        # Look for word numbers
        word_to_num = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'fifteen': 15, 'twenty': 20
        }
        
        lower_text = years_text.lower()
        for word, num in word_to_num.items():
            if word in lower_text:
                return num
        
        return None
    
    def validate_extraction(self, extracted_data: Dict[str, Any], 
                          expected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data against expected values"""
        
        validation_results = {
            'matches': {},
            'mismatches': {},
            'missing': [],
            'accuracy': 0.0
        }
        
        # Check each expected field
        for field, expected_value in expected_data.items():
            if field in extracted_data:
                actual_value = extracted_data[field]
                
                # Normalize for comparison
                if isinstance(expected_value, str) and isinstance(actual_value, str):
                    match = expected_value.lower().strip() == actual_value.lower().strip()
                else:
                    match = expected_value == actual_value
                
                if match:
                    validation_results['matches'][field] = actual_value
                else:
                    validation_results['mismatches'][field] = {
                        'expected': expected_value,
                        'actual': actual_value
                    }
            else:
                validation_results['missing'].append(field)
        
        # Calculate accuracy
        total_fields = len(expected_data)
        if total_fields > 0:
            matches = len(validation_results['matches'])
            validation_results['accuracy'] = matches / total_fields
        
        return validation_results
    
    def extract_and_save(self, pdf_path: str, output_path: str) -> bool:
        """Extract form data and save to JSON file"""
        
        try:
            # Extract all fields
            extracted = self.extract_all_fields(pdf_path)
            
            # Save to JSON
            with open(output_path, 'w') as f:
                json.dump(extracted, f, indent=2)
            
            logger.info(f"Saved extracted data to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving extracted data: {e}")
            return False


def test_extractor():
    """Test the PDF form extractor"""
    
    extractor = PDFFormExtractor()
    
    # Test with a sample PDF
    test_pdf = "/tmp/questionnaire.pdf"
    
    if os.path.exists(test_pdf):
        # Extract form data
        data = extractor.extract_all_fields(test_pdf)
        
        print("Extracted Form Data:")
        print(json.dumps(data, indent=2))
        
        # Save to file
        output_path = "/tmp/extracted_form_data.json"
        extractor.extract_and_save(test_pdf, output_path)
        
        # Validate if we have expected data
        expected = {
            'red_seal_status': 'Yes',
            'trade_licenses': ['Electrical', 'HVAC'],
            'years_experience': 5
        }
        
        if 'questionnaire_data' in data:
            validation = extractor.validate_extraction(
                data['questionnaire_data'], 
                expected
            )
            print("\nValidation Results:")
            print(json.dumps(validation, indent=2))
    else:
        print(f"Test PDF not found: {test_pdf}")


if __name__ == "__main__":
    test_extractor()