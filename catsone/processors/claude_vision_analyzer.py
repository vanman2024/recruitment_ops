#!/usr/bin/env python3
"""
Claude 4 Opus Vision-based Questionnaire Analyzer
Uses Claude 4 Opus for superior checkbox and radio button detection
"""

import os
import logging
import base64
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from PIL import Image

logger = logging.getLogger(__name__)

class ClaudeVisionAnalyzer:
    """Analyze questionnaire images using Claude 4 Opus for best accuracy"""
    
    def __init__(self, anthropic_api_key: str = None):
        # Always try to get from environment if not provided
        self.api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.error("No Anthropic API key provided")
        self.model = "claude-opus-4-20250514"  # Claude 4 Opus - The model you specified
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def analyze_questionnaire_images(self, image_folder: str) -> Dict[str, Any]:
        """Analyze all questionnaire images to extract actual selections"""
        
        # Ensure we have the API key
        if not self.api_key or self.api_key == "your-api-key-here":
            logger.error("Invalid Claude API key - using environment variable")
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
            if not self.api_key or 'your-api-key' in self.api_key:
                logger.error("No valid Claude API key found")
                return self._get_fallback_analysis()
        
        try:
            # Get all image files
            image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
            image_files.sort()  # Ensure proper page order
            
            # Process pages in batches for speed
            import concurrent.futures
            page_analyses = []
            
            # Process up to 3 pages in parallel to speed up while maintaining rate limits
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Create tasks for each page
                future_to_page = {}
                for image_file in image_files:
                    image_path = os.path.join(image_folder, image_file)
                    future = executor.submit(self._analyze_single_page, image_path)
                    future_to_page[future] = image_file
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_page):
                    page_file = future_to_page[future]
                    try:
                        page_analysis = future.result()
                        page_analyses.append({
                            'page': page_file,
                            'analysis': page_analysis
                        })
                    except Exception as e:
                        logger.error(f"Error analyzing {page_file}: {e}")
                        page_analyses.append({
                            'page': page_file,
                            'analysis': {'error': str(e)}
                        })
            
            # Sort by page name to maintain order
            page_analyses.sort(key=lambda x: x['page'])
            
            # Combine all pages into complete profile
            complete_analysis = self._combine_page_analyses(page_analyses)
            
            return {
                'candidate_profile': complete_analysis,
                'page_analyses': page_analyses,
                'analysis_timestamp': datetime.now().isoformat(),
                'method': 'claude_4_opus_vision'
            }
            
        except Exception as e:
            logger.error(f"Error in Claude vision analysis: {e}")
            return {'error': str(e)}
    
    def _analyze_single_page(self, image_path: str) -> Dict[str, Any]:
        """Analyze a single page image using Claude 4 Opus"""
        
        try:
            # Load and encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create detailed prompt for Claude 4 Opus
            prompt = """You are analyzing a page from a Dayforce questionnaire form. Extract ALL information comprehensively.

CRITICAL INSTRUCTIONS FOR RADIO BUTTONS AND CHECKBOXES:

1. RADIO BUTTONS (circular options):
   - In Dayforce forms, selected radio buttons have a DARKER FILL in the center
   - Look carefully - the selected option will have a filled/darker center
   - Empty radio buttons appear as empty circles
   - IMPORTANT: These are REQUIRED fields, so one option MUST be selected

2. CHECKBOXES (square options):
   - Selected checkboxes have visible checkmarks (✓ or ✔ or X)
   - Empty checkboxes appear as empty squares

FOR EACH QUESTION ON THIS PAGE:

1. Question Details:
   - Exact question number and complete text
   - Question type (radio buttons, checkboxes, dropdown, text field)

2. All Available Options:
   - List EVERY option shown (whether selected or not)

3. Actual Selections (CRITICAL):
   - For radio buttons: The one with darker fill
   - For checkboxes: Those with visible checkmarks
   - For dropdowns: The displayed value
   - For text fields: Any written text

4. Equipment Questions:
   - List all equipment brands and types
   - Note which are selected

Return as JSON:
{
    "questions_and_responses": [
        {
            "question_number": "10",
            "question_text": "Do you have your Red Seal?",
            "question_type": "radio_button",
            "all_available_options": ["Yes", "No"],
            "actual_selections": ["Yes"],  // The one with darker fill
            "equipment_specific": {
                "is_equipment_question": false
            }
        }
    ]
}

Remember: Radio buttons in Dayforce forms show selection as a darker filled center, not an empty circle."""
            
            headers = {
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # Send to Claude 4 Opus
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_claude_response(result['content'][0]['text'])
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return {'error': f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {'error': str(e)}
    
    def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response"""
        
        try:
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback parsing
                logger.warning("Could not extract JSON from Claude response")
                return {'raw_response': response_text}
                
        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            return {'raw_response': response_text, 'parse_error': str(e)}
    
    def _combine_page_analyses(self, page_analyses: List[Dict]) -> Dict[str, Any]:
        """Combine analyses from all pages into a complete profile"""
        
        profile = {
            'personal_info': {},
            'certifications': {},
            'equipment_experience': {
                'brands_worked_with': [],
                'equipment_types': [],
                'specific_experience': []
            },
            'work_preferences': {},
            'skills': {},
            'all_responses': []
        }
        
        for page_data in page_analyses:
            page_analysis = page_data.get('analysis', {})
            
            if 'questions_and_responses' in page_analysis:
                for q in page_analysis['questions_and_responses']:
                    # Store all responses
                    profile['all_responses'].append(q)
                    
                    # Extract specific information
                    question_text = (q.get('question_text') or '').lower()
                    selections = q.get('actual_selections', [])
                    
                    # Certifications
                    if 'red seal' in question_text and selections:
                        profile['certifications']['red_seal'] = selections[0]
                    elif 'journeyman' in question_text and selections:
                        profile['certifications']['journeyman_license'] = selections[0]
                    
                    # Equipment
                    equipment_info = q.get('equipment_specific', {})
                    if equipment_info.get('is_equipment_question'):
                        profile['equipment_experience']['brands_worked_with'].extend(
                            equipment_info.get('equipment_brands_selected', [])
                        )
                        profile['equipment_experience']['equipment_types'].extend(
                            equipment_info.get('equipment_types_selected', [])
                        )
                    
                    # Work preferences
                    if 'shift' in question_text and 'rotation' in question_text and selections:
                        profile['work_preferences']['shift_rotation'] = selections[0]
                    elif 'field' in question_text and selections:
                        profile['work_preferences']['field_work'] = selections[0]
        
        # Remove duplicates
        for key in ['brands_worked_with', 'equipment_types', 'specific_experience']:
            profile['equipment_experience'][key] = list(set(profile['equipment_experience'][key]))
        
        return profile
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return a fallback analysis when API key is invalid"""
        return {
            'error': 'Claude API key invalid - please check your .env file',
            'certifications': {
                'red_seal': 'Unable to detect - API key error',
                'journeyman_license': 'Unable to detect - API key error'
            },
            'equipment_experience': {
                'brands_worked_with': [],
                'equipment_types': [],
                'specific_experience': []
            },
            'work_preferences': {},
            'skills': {},
            'all_responses': []
        }