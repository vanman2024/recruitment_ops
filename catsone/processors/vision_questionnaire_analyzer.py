#!/usr/bin/env python3
"""
Vision-based Questionnaire Analyzer
Uses Gemini Vision to detect actual checkmarks and selections from questionnaire images
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)

class VisionQuestionnaireAnalyzer:
    """Analyze questionnaire images to detect actual selections and checkmarks"""
    
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_questionnaire_images(self, image_folder: str) -> Dict[str, Any]:
        """Analyze all questionnaire images to extract actual selections"""
        
        try:
            # Get all image files
            image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
            image_files.sort()  # Ensure proper page order
            
            # Analyze each page
            page_analyses = []
            for image_file in image_files:
                image_path = os.path.join(image_folder, image_file)
                page_analysis = self._analyze_single_page(image_path)
                page_analyses.append({
                    'page': image_file,
                    'analysis': page_analysis
                })
            
            # Combine all pages into complete profile
            complete_analysis = self._combine_page_analyses(page_analyses)
            
            return {
                'candidate_profile': complete_analysis,
                'page_analyses': page_analyses,
                'analysis_timestamp': datetime.now().isoformat(),
                'method': 'gemini_vision'
            }
            
        except Exception as e:
            logger.error(f"Error in vision analysis: {e}")
            return {'error': str(e)}
    
    def _analyze_single_page(self, image_path: str) -> Dict[str, Any]:
        """Analyze a single page image to extract selections"""
        
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Create detailed prompt for comprehensive vision analysis
            prompt = f"""
            You are analyzing page of a filled questionnaire form. Extract EVERYTHING comprehensively.
            
            CRITICAL: PAY EXTREME ATTENTION TO RADIO BUTTONS AND CHECKMARKS!
            
            FOR RADIO BUTTONS (VERY IMPORTANT):
            - Look for SUBTLE differences between selected and unselected radio buttons
            - Selected radio button may appear as: filled circle (●), darker circle, circle with dot inside (⦿)
            - Unselected radio button appears as: empty circle (○)
            - IMPORTANT: In some forms, the difference is VERY SUBTLE - a slightly darker shade
            - Look for ANY visual difference in the radio button circles, even minimal shading
            
            FOR CHECKBOXES:
            - Empty checkbox: □ or ☐ (NOT selected)
            - Checked checkbox: ☑ or ☒ or ✓ or ✔ or X or filled square
            
            Only include items in "actual_selections" if they have a VISIBLE checkmark or selection!

            FOR EACH QUESTION ON THIS PAGE, provide:

            1. QUESTION DETAILS:
               - Exact question number
               - Complete question text (word for word)
               - Question type (checkbox list, radio button, text field, dropdown, etc.)

            2. ALL AVAILABLE OPTIONS (VERY IMPORTANT):
               - List EVERY checkbox option shown (whether checked or not)
               - List EVERY radio button option shown
               - List EVERY dropdown option if visible
               - Include any "Other" or write-in options

            3. ACTUAL SELECTIONS (CRITICAL - LOOK CAREFULLY):
               - For checkboxes: Look for ✓, ✔, X, or filled/darkened squares
               - For radio buttons: Look for filled circles (●) vs empty circles (○)
               - IMPORTANT: Only list options that have VISIBLE check marks or selections
               - If a checkbox is empty/unchecked, do NOT include it in actual_selections
               - For dropdowns: Note the displayed/selected value
               - Include any text written in text fields

            4. EQUIPMENT-SPECIFIC EXTRACTION:
               If the question involves equipment, machinery, or brands:
               - List ALL equipment brands shown (CAT, Komatsu, John Deere, Hitachi, Volvo, etc.)
               - List ALL equipment types shown (excavators, loaders, dozers, graders, etc.)
               - Note which ones are SELECTED vs just available options
               - Extract any written equipment experience details

            Return as detailed JSON:
            {{
                "page_type": "General Information / Legal / Skills / Employment / Preferences",
                "candidate_name": "if visible",
                "questions_and_responses": [
                    {{
                        "question_number": "1",
                        "question_text": "Complete question text here",
                        "question_type": "checkbox_list",
                        "all_available_options": [
                            "Option 1 (whether checked or not)",
                            "Option 2 (whether checked or not)",
                            "Option 3 (whether checked or not)"
                        ],
                        "actual_selections": [
                            "Only the ones actually checked"
                        ],
                        "text_responses": ["Any text written"],
                        "equipment_specific": {{
                            "is_equipment_question": true/false,
                            "equipment_brands_shown": ["CAT", "Komatsu", etc.],
                            "equipment_brands_selected": ["Only selected ones"],
                            "equipment_types_shown": ["Excavator", "Loader", etc.],
                            "equipment_types_selected": ["Only selected ones"]
                        }}
                    }}
                ]
            }}

            BE EXTREMELY THOROUGH. Extract every option shown, not just selected ones.
            """
            
            # Send to Gemini Vision
            response = self.model.generate_content([prompt, image])
            
            return self._parse_vision_response(response.text)
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {'error': str(e)}
    
    def _parse_vision_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini Vision response"""
        
        try:
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON, parse as text
                return {'vision_analysis': response_text}
                
        except Exception as e:
            return {'vision_response': response_text, 'parse_error': str(e)}
    
    def _combine_page_analyses(self, page_analyses: List[Dict]) -> Dict[str, Any]:
        """Combine all page analyses into complete candidate profile"""
        
        combined = {
            'candidate_info': {},
            'actual_responses': {},
            'response_summary': {},
            'equipment_analysis': {
                'brands_available': [],
                'brands_selected': [],
                'equipment_types_available': [],
                'equipment_types_selected': [],
                'equipment_gaps': []
            }
        }
        
        for page_data in page_analyses:
            analysis = page_data.get('analysis', {})
            
            # Extract candidate name if found
            if 'candidate_name' in analysis and analysis['candidate_name']:
                combined['candidate_info']['name'] = analysis['candidate_name']
            
            # Process questions and responses
            questions = analysis.get('questions_and_responses', [])
            for q in questions:
                question_num = q.get('question_number')
                question_text = q.get('question_text', '')
                actual_selections = q.get('actual_selections', [])
                text_responses = q.get('text_responses', [])
                
                # Store actual responses
                response_key = f"q{question_num}_{self._categorize_question(question_text)}"
                combined['actual_responses'][response_key] = {
                    'question': question_text,
                    'selections': actual_selections,
                    'text': text_responses,
                    'type': q.get('response_type'),
                    'all_options': q.get('all_available_options', [])
                }
                
                # Extract equipment data
                equipment_data = q.get('equipment_specific', {})
                if equipment_data.get('is_equipment_question'):
                    # Collect available brands/types
                    brands_shown = equipment_data.get('equipment_brands_shown', [])
                    combined['equipment_analysis']['brands_available'].extend(brands_shown)
                    
                    types_shown = equipment_data.get('equipment_types_shown', [])
                    combined['equipment_analysis']['equipment_types_available'].extend(types_shown)
                    
                    # Collect selected brands/types
                    brands_selected = equipment_data.get('equipment_brands_selected', [])
                    combined['equipment_analysis']['brands_selected'].extend(brands_selected)
                    
                    types_selected = equipment_data.get('equipment_types_selected', [])
                    combined['equipment_analysis']['equipment_types_selected'].extend(types_selected)
        
        # Remove duplicates from equipment lists
        for key in combined['equipment_analysis']:
            if isinstance(combined['equipment_analysis'][key], list):
                combined['equipment_analysis'][key] = list(set(combined['equipment_analysis'][key]))
        
        # Calculate equipment gaps
        combined['equipment_analysis']['equipment_gaps'] = [
            brand for brand in combined['equipment_analysis']['brands_available']
            if brand not in combined['equipment_analysis']['brands_selected']
        ]
        
        # Create summary
        combined['response_summary'] = self._create_response_summary(combined['actual_responses'])
        
        return combined
    
    def _categorize_question(self, question_text: str) -> str:
        """Categorize question for easier reference"""
        
        if not question_text:
            return 'unknown'
        
        text_lower = question_text.lower()
        
        if 'industries' in text_lower:
            return 'industries_worked'
        elif 'fast-paced' in text_lower:
            return 'fast_paced_comfort'
        elif 'physical' in text_lower and 'limitations' in text_lower:
            return 'physical_limitations'
        elif 'mining experience' in text_lower:
            return 'mining_experience'
        elif 'position' in text_lower and 'interested' in text_lower:
            return 'positions_interested'
        elif 'winter' in text_lower and 'gear' in text_lower:
            return 'weather_gear'
        elif 'rotational shifts' in text_lower:
            return 'rotational_shifts'
        elif 'service truck' in text_lower:
            return 'service_truck_sharing'
        elif 'background check' in text_lower:
            return 'background_check'
        elif 'drug' in text_lower and 'test' in text_lower:
            return 'drug_test'
        elif 'komatsu' in text_lower:
            return 'komatsu_experience'
        elif 'red seal' in text_lower:
            return 'red_seal'
        elif 'journeyman' in text_lower:
            return 'journeyman_license'
        elif 'underground' in text_lower and 'brands' in text_lower:
            return 'underground_brands'
        elif 'employment status' in text_lower:
            return 'employment_status'
        elif 'available to start' in text_lower:
            return 'start_availability'
        elif 'new opportunity' in text_lower:
            return 'reason_for_looking'
        else:
            return 'other'
    
    def _create_response_summary(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Create human-readable summary of actual responses"""
        
        summary = {
            'key_qualifications': [],
            'experience_highlights': [],
            'work_preferences': [],
            'potential_concerns': []
        }
        
        for key, response in responses.items():
            selections = response.get('selections', [])
            text = response.get('text', [])
            
            # Process based on question type
            if 'industries_worked' in key and selections:
                summary['experience_highlights'].append(f"Industries: {', '.join(selections)}")
            
            elif 'red_seal' in key and 'Yes' in selections:
                summary['key_qualifications'].append('Red Seal Certified')
            
            elif 'journeyman' in key and 'Yes' in selections:
                summary['key_qualifications'].append('Journeyman Licensed')
            
            elif 'mining_experience' in key and 'Yes' in selections:
                summary['experience_highlights'].append('Has mining experience')
                if text:
                    summary['experience_highlights'].append(f"Mining comment: {', '.join(text)}")
            
            elif 'positions_interested' in key and selections:
                summary['work_preferences'].append(f"Interested positions: {', '.join(selections[:3])}...")
            
            elif 'underground_brands' in key:
                if 'None' in str(selections):
                    summary['potential_concerns'].append('No underground machinery brand experience')
                elif selections:
                    summary['experience_highlights'].append(f"Underground brands: {', '.join(selections)}")
            
            elif 'reason_for_looking' in key and selections:
                summary['work_preferences'].append(f"Reason for change: {', '.join(selections)}")
        
        return summary


# Test the vision analyzer
if __name__ == "__main__":
    import os
    
    # Get Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("GEMINI_API_KEY environment variable not set")
        exit(1)
    
    # Analyze the questionnaire images
    analyzer = VisionQuestionnaireAnalyzer(gemini_key)
    result = analyzer.analyze_questionnaire_images('questionnaire_images')
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print("=== VISION-BASED QUESTIONNAIRE ANALYSIS ===")
        
        candidate_profile = result['candidate_profile']
        
        # Print candidate info
        candidate_info = candidate_profile.get('candidate_info', {})
        print(f"Candidate: {candidate_info.get('name', 'Unknown')}")
        print()
        
        # Print actual responses (first 5)
        actual_responses = candidate_profile.get('actual_responses', {})
        print("=== ACTUAL SELECTIONS (First 5) ===")
        for i, (key, response) in enumerate(actual_responses.items()):
            if i >= 5:
                break
            print(f"{key}:")
            print(f"  Question: {response['question'][:100]}...")
            print(f"  Selections: {response['selections']}")
            if response['text']:
                print(f"  Text: {response['text']}")
            print()
        
        # Print summary
        summary = candidate_profile.get('response_summary', {})
        print("=== RESPONSE SUMMARY ===")
        for category, items in summary.items():
            if items:
                print(f"{category.upper()}:")
                for item in items:
                    print(f"  • {item}")
                print()