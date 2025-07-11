#!/usr/bin/env python3
"""
Focused checkbox analyzer - specifically tuned for questionnaire forms
"""

import os
import sys
import logging
from typing import Dict, List, Any
import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)

class FocusedCheckboxAnalyzer:
    """Accurate checkbox detection for questionnaires"""
    
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def analyze_candidate_folder(self, candidate_folder: str) -> Dict[str, Any]:
        """Analyze all pages in a candidate's folder"""
        
        # Key questions we care about
        key_questions = {
            'red_seal': 'Do you have a Red Seal certification?',
            'industries': 'What are the main industries you have worked in?',
            'availability': 'When would you be available to start work?',
            'why_looking': 'Why are you looking for a new opportunity?',
            'equipment_experience': 'equipment experience',
            'position': 'Which position(s) are you interested in?'
        }
        
        results = {
            'candidate_id': os.path.basename(candidate_folder),
            'responses': {}
        }
        
        # Process each page
        pages = sorted([f for f in os.listdir(candidate_folder) if f.endswith('.png')])
        
        for page_file in pages:
            page_path = os.path.join(candidate_folder, page_file)
            page_results = self._analyze_page_focused(page_path, key_questions)
            results['responses'].update(page_results)
        
        return results
    
    def _analyze_page_focused(self, image_path: str, key_questions: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a single page focusing on key questions"""
        
        try:
            image = Image.open(image_path)
            
            # Very specific prompt for accuracy
            prompt = """
            You are analyzing a questionnaire form. I need EXACT visual detection of checkboxes and radio buttons.
            
            VISUAL INDICATORS TO LOOK FOR:
            - Filled radio button: A dark filled circle (●)
            - Empty radio button: An empty circle (○)
            - Checked checkbox: Has a checkmark (✓) or X inside
            - Empty checkbox: Empty square (☐)
            
            For these specific questions, tell me EXACTLY what you see:
            
            1. "Do you have a Red Seal certification?" or "Do you have your Red Seal?"
               - Look for Yes/No radio buttons
               - Which one has the filled circle (●)?
            
            2. "What are the main industries you have worked in?"
               - List which checkboxes have marks
            
            3. "When would you be available to start work?"
               - What option is selected?
            
            4. "Why are you looking for a new opportunity?"
               - What option is selected?
            
            5. Any question about equipment experience
               - What is written or selected?
            
            For EACH question found:
            - State if you see filled (●) or empty (○) radio buttons
            - State if you see checked (✓) or empty (☐) checkboxes
            - Quote any written text exactly
            
            BE VERY SPECIFIC about the visual state - don't interpret, just report what you see.
            """
            
            response = self.model.generate_content([prompt, image])
            return self._parse_focused_response(response.text)
            
        except Exception as e:
            logger.error(f"Error analyzing {image_path}: {e}")
            return {}
    
    def _parse_focused_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the focused response"""
        
        results = {}
        
        # Look for Red Seal
        if 'red seal' in response_text.lower():
            if '● yes' in response_text.lower() or 'filled circle next to yes' in response_text.lower():
                results['red_seal'] = 'YES'
            elif '● no' in response_text.lower() or 'filled circle next to no' in response_text.lower():
                results['red_seal'] = 'NO'
            else:
                results['red_seal'] = 'Not selected'
        
        # Extract other key information
        lines = response_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            
            # Industries
            if 'industries' in line_lower and 'worked' in line_lower:
                # Look for the next lines that mention checked items
                results['industries'] = []
                # Parse following lines for checked items
            
            # Availability
            if 'available to start' in line_lower:
                if 'within 1 month' in line_lower:
                    results['availability'] = 'Within 1 month'
                elif 'immediately' in line_lower:
                    results['availability'] = 'Immediately'
            
            # Why looking
            if 'looking for' in line_lower and 'opportunity' in line_lower:
                if 'work-life balance' in line_lower:
                    results['why_looking'] = 'Work-Life Balance'
        
        return results


def analyze_questionnaire(candidate_folder: str) -> Dict[str, Any]:
    """Main function to analyze a candidate's questionnaire"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not set")
    
    analyzer = FocusedCheckboxAnalyzer(gemini_key)
    return analyzer.analyze_candidate_folder(candidate_folder)