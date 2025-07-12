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
            
            # Create enhanced detailed prompt for Claude 4 Opus
            prompt = """You are analyzing a page from a Dayforce questionnaire form that may have been enhanced for better form detection. 

IMPORTANT: This image may be an ENHANCED VERSION specifically processed to improve checkbox and radio button visibility:
- The image may have increased contrast to make subtle selections more visible
- Dark fills may appear more pronounced than in the original
- Edge detection may have been applied to highlight form boundaries
- Binary thresholding may make selections appear as pure black/white

CRITICAL RULES FOR ENHANCED IMAGES:
1. ONLY report what you can actually SEE on the form
2. DO NOT make assumptions or add information not visible
3. If enhanced processing made empty fields appear filled, DO NOT report them as selected
4. Look for CONSISTENT patterns - true selections will appear across enhancement types
5. Use TWO-PASS ANALYSIS: First scan for obvious selections, then carefully verify subtle ones

ENHANCED DETECTION INSTRUCTIONS:

1. RADIO BUTTONS (circular options) - ENHANCED VERSION:
   - In enhanced images, selected radio buttons may appear as SOLID BLACK DOTS
   - Look for clear circular fills or dots within the radio button boundaries
   - Enhanced contrast may make even faint selections appear very dark
   - RED SEAL QUESTION VERIFICATION: 
     * Always appears as "Do you have your Red Seal?" with Yes/No radio buttons
     * Position: FIRST radio button = "Yes", SECOND = "No"
     * Enhanced images: Look for ANY solid fill/dot in the circles
     * Cross-reference: If enhancement made both appear filled, use context clues
     * CONFIDENCE SCORING: Rate your confidence 1-10 for each selection

2. CHECKBOXES (square options) - ENHANCED VERSION:
   - Enhanced images may show checkmarks as solid black marks or X's
   - Look for clear geometric shapes within checkbox boundaries
   - Distinguish between enhancement artifacts and actual checkmarks
   - True checkmarks will have consistent shape/pattern

3. TWO-PASS ANALYSIS REQUIREMENT:
   
   FIRST PASS - Obvious Selections:
   - Scan for clearly visible, unambiguous markings
   - Document only selections you're 100% certain about
   
   SECOND PASS - Careful Verification:
   - Re-examine subtle or questionable markings
   - Use surrounding context to verify selections
   - Apply confidence scoring for borderline cases

FOR EACH QUESTION ON THIS PAGE:

1. Question Details:
   - Exact question number and complete text
   - Question type (radio buttons, checkboxes, dropdown, text field)
   - Image enhancement level detected (normal/high_contrast/binary/edge_enhanced)

2. All Available Options:
   - List EVERY option shown (whether selected or not)

3. Selection Analysis (CRITICAL - ENHANCED APPROACH):
   - PRIMARY SELECTIONS: Those with 90-100% confidence
   - PROBABLE SELECTIONS: Those with 70-89% confidence  
   - QUESTIONABLE: Those with 50-69% confidence
   - For each selection, provide confidence score (1-10)

4. Enhanced Image Considerations:
   - Note if image appears to be contrast-enhanced
   - Identify any potential enhancement artifacts
   - Flag selections that may be questionable due to enhancement

SPECIAL ATTENTION FOR TRADE LICENSES - ENHANCED DETECTION:
- Look for the trade license question with long checkbox list
- Enhanced images may make checkmarks more visible
- SCAN SYSTEMATICALLY: Go row by row through the entire list
- Look for solid black squares, checkmarks, or X marks
- Even faint marks may appear enhanced - verify with confidence scoring
- Common trades to watch for:
  * Truck and Transport Mechanic
  * Transport Trailer Technician  
  * Heavy Equipment Technician
  * Automotive Service Technician
  * Millwright
  * Welder
  * Electrician
  * And 20+ others...

ENHANCED JSON RESPONSE FORMAT:
{
    "image_analysis_meta": {
        "enhancement_level_detected": "high_contrast" | "binary" | "edge_enhanced" | "normal",
        "analysis_confidence": 8.5,
        "two_pass_completed": true
    },
    "questions_and_responses": [
        {
            "question_number": "10",
            "question_text": "Do you have your Red Seal?",
            "question_type": "radio_button",
            "all_available_options": ["Yes", "No"],
            "selection_analysis": {
                "primary_selections": ["Yes"],
                "confidence_scores": {"Yes": 9, "No": 1},
                "enhancement_artifacts_noted": false
            },
            "equipment_specific": {
                "is_equipment_question": false
            }
        }
    ],
    "verification_notes": {
        "red_seal_verification": "Clear dark fill in first radio button, high confidence",
        "trade_licenses_count": 2,
        "questionable_selections": []
    }
}

FINAL VERIFICATION STEP:
Before submitting, ask yourself:
1. Do my selections make logical sense for a job questionnaire?
2. Did I check the entire trade license list thoroughly?
3. Are my confidence scores realistic for the image quality?
4. Did I account for potential enhancement artifacts?

Remember: Enhanced images are designed to make subtle selections more visible, but may also amplify noise. Use careful judgment and confidence scoring."""
            
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
        """Combine analyses from all pages into a complete profile with enhanced confidence tracking"""
        
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
            'all_responses': [],
            'confidence_metadata': {
                'overall_confidence': 0.0,
                'enhancement_levels': [],
                'high_confidence_selections': [],
                'questionable_selections': []
            }
        }
        
        total_confidence = 0.0
        confidence_count = 0
        
        for page_data in page_analyses:
            page_analysis = page_data.get('analysis', {})
            
            # Track enhancement metadata
            if 'image_analysis_meta' in page_analysis:
                meta = page_analysis['image_analysis_meta']
                profile['confidence_metadata']['enhancement_levels'].append(
                    meta.get('enhancement_level_detected', 'unknown')
                )
                total_confidence += meta.get('analysis_confidence', 0.0)
                confidence_count += 1
            
            if 'questions_and_responses' in page_analysis:
                for q in page_analysis['questions_and_responses']:
                    # Store all responses
                    profile['all_responses'].append(q)
                    
                    # Extract specific information
                    question_text = (q.get('question_text') or '').lower()
                    
                    # Handle enhanced response format
                    if 'selection_analysis' in q:
                        selections = q['selection_analysis'].get('primary_selections', [])
                        confidence_scores = q['selection_analysis'].get('confidence_scores', {})
                        
                        # Track high/low confidence selections
                        for selection, score in confidence_scores.items():
                            if score >= 8:
                                profile['confidence_metadata']['high_confidence_selections'].append({
                                    'question': question_text,
                                    'selection': selection,
                                    'confidence': score
                                })
                            elif score <= 6:
                                profile['confidence_metadata']['questionable_selections'].append({
                                    'question': question_text,
                                    'selection': selection,
                                    'confidence': score
                                })
                    else:
                        # Fallback to old format
                        selections = q.get('actual_selections', [])
                    
                    # Certifications - Enhanced extraction
                    if 'red seal' in question_text:
                        if selections:
                            profile['certifications']['red_seal'] = selections[0]
                            
                            # Add confidence info if available
                            if 'selection_analysis' in q:
                                confidence = q['selection_analysis'].get('confidence_scores', {}).get(selections[0], 0)
                                profile['certifications']['red_seal_confidence'] = confidence
                                logger.info(f"Extracted Red Seal: {selections[0]} (confidence: {confidence}) from enhanced analysis")
                            else:
                                logger.info(f"Extracted Red Seal: {selections[0]} from question '{q.get('question_text')}'")
                        else:
                            logger.warning(f"Red Seal question found but no selection detected: {q}")
                    
                    elif 'journeyman' in question_text or 'trades are you licensed' in question_text:
                        if selections:
                            # This is likely a multi-select checkbox question
                            profile['certifications']['journeyman_licenses'] = selections
                            
                            # Add confidence tracking for trade licenses
                            if 'selection_analysis' in q:
                                confidence_scores = q['selection_analysis'].get('confidence_scores', {})
                                high_confidence_trades = [
                                    trade for trade, score in confidence_scores.items() 
                                    if score >= 7 and trade in selections
                                ]
                                profile['certifications']['high_confidence_trades'] = high_confidence_trades
                                logger.info(f"Extracted journeyman licenses: {selections} (high confidence: {high_confidence_trades})")
                            else:
                                logger.info(f"Extracted journeyman licenses: {selections}")
                        else:
                            logger.warning(f"Journeyman license question found but no selections: {q}")
                    
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
        
        # Calculate overall confidence
        if confidence_count > 0:
            profile['confidence_metadata']['overall_confidence'] = total_confidence / confidence_count
        
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