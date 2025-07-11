#!/usr/bin/env python3
"""
Special handler for Dayforce questionnaire PDFs
Handles the limitation where radio button selections are too subtle for vision detection
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DayforceQuestionnaireHandler:
    """
    Special handler for Dayforce questionnaires with known limitations
    """
    
    def __init__(self):
        self.known_limitations = [
            "Radio button selections appear as subtle shading differences",
            "Selected vs unselected radio buttons are visually nearly identical",
            "Checkboxes with checkmarks (✓) are reliably detected",
            "Text fields and dropdowns are reliably extracted"
        ]
    
    def process_dayforce_questionnaire(self, vision_result: Dict[str, Any], 
                                     manual_overrides: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process Dayforce questionnaire with special handling for radio buttons
        
        Args:
            vision_result: Result from vision analyzer
            manual_overrides: Manual corrections for radio button questions
        
        Returns:
            Enhanced result with warnings and manual data
        """
        
        # Start with vision results
        enhanced_result = vision_result.copy()
        
        # Add warning about Dayforce limitations
        enhanced_result['dayforce_warning'] = {
            'detected': True,
            'message': "IMPORTANT: Dayforce PDF radio button selections cannot be reliably detected due to minimal visual differences.",
            'affected_questions': [],
            'manual_verification_required': True
        }
        
        # Identify radio button questions that need manual verification
        radio_questions = []
        if 'page_analyses' in vision_result:
            for page_data in vision_result['page_analyses']:
                page_analysis = page_data.get('analysis', {})
                if 'questions_and_responses' in page_analysis:
                    for q in page_analysis['questions_and_responses']:
                        if q.get('question_type') == 'radio_button':
                            # Check if selection was detected
                            if not q.get('actual_selections'):
                                radio_questions.append({
                                    'question_number': q.get('question_number'),
                                    'question_text': q.get('question_text'),
                                    'options': q.get('all_available_options', [])
                                })
        
        enhanced_result['dayforce_warning']['affected_questions'] = radio_questions
        
        # Apply manual overrides if provided
        if manual_overrides:
            enhanced_result['manual_corrections'] = manual_overrides
            self._apply_manual_overrides(enhanced_result, manual_overrides)
        
        # Extract key information with fallbacks
        candidate_profile = enhanced_result.get('candidate_profile', {})
        
        # Handle critical questions with defaults or prompts
        critical_questions = {
            'red_seal': self._extract_red_seal(enhanced_result, manual_overrides),
            'journeyman_license': self._extract_journeyman(enhanced_result, manual_overrides),
            'equipment_experience': self._extract_equipment(enhanced_result),
            'work_preferences': self._extract_work_preferences(enhanced_result)
        }
        
        candidate_profile.update(critical_questions)
        enhanced_result['candidate_profile'] = candidate_profile
        
        # Generate human-readable summary
        enhanced_result['extraction_summary'] = self._generate_summary(enhanced_result)
        
        return enhanced_result
    
    def _extract_red_seal(self, result: Dict, overrides: Optional[Dict]) -> Optional[str]:
        """Extract Red Seal status with fallback to manual override"""
        
        # Check manual override first
        if overrides and 'red_seal' in overrides:
            return overrides['red_seal']
        
        # Try to find in vision results
        if 'page_analyses' in result:
            for page_data in result['page_analyses']:
                page_analysis = page_data.get('analysis', {})
                if 'questions_and_responses' in page_analysis:
                    for q in page_analysis['questions_and_responses']:
                        question_text = q.get('question_text') or ''
                        if 'red seal' in question_text.lower():
                            selections = q.get('actual_selections', [])
                            if selections:
                                return selections[0]
        
        return "REQUIRES MANUAL VERIFICATION"
    
    def _extract_journeyman(self, result: Dict, overrides: Optional[Dict]) -> Optional[str]:
        """Extract Journeyman license status with fallback to manual override"""
        
        # Check manual override first
        if overrides and 'journeyman_license' in overrides:
            return overrides['journeyman_license']
        
        # Try to find in vision results
        if 'page_analyses' in result:
            for page_data in result['page_analyses']:
                page_analysis = page_data.get('analysis', {})
                if 'questions_and_responses' in page_analysis:
                    for q in page_analysis['questions_and_responses']:
                        question_text = q.get('question_text') or ''
                        if 'journeyman' in question_text.lower():
                            selections = q.get('actual_selections', [])
                            if selections:
                                return selections[0]
        
        return "REQUIRES MANUAL VERIFICATION"
    
    def _extract_equipment(self, result: Dict) -> Dict[str, List[str]]:
        """Extract equipment experience - this usually works well with checkboxes"""
        
        equipment_data = {
            'brands_worked_with': [],
            'equipment_types': [],
            'specific_experience': []
        }
        
        if 'page_analyses' in result:
            for page_data in result['page_analyses']:
                page_analysis = page_data.get('analysis', {})
                if 'questions_and_responses' in page_analysis:
                    for q in page_analysis['questions_and_responses']:
                        # Check for equipment-specific questions
                        equipment_info = q.get('equipment_specific', {})
                        if equipment_info.get('is_equipment_question'):
                            equipment_data['brands_worked_with'].extend(
                                equipment_info.get('equipment_brands_selected', [])
                            )
                            equipment_data['equipment_types'].extend(
                                equipment_info.get('equipment_types_selected', [])
                            )
                        
                        # Also check for underground machinery question
                        question_text = q.get('question_text') or ''
                        if 'underground machinery' in question_text.lower():
                            equipment_data['specific_experience'].extend(
                                q.get('actual_selections', [])
                            )
        
        # Remove duplicates
        for key in equipment_data:
            equipment_data[key] = list(set(equipment_data[key]))
        
        return equipment_data
    
    def _extract_work_preferences(self, result: Dict) -> Dict[str, Any]:
        """Extract work preferences from reliably detected fields"""
        
        preferences = {
            'shift_rotation': None,
            'field_work': None,
            'extended_periods': None,
            'shared_housing': None
        }
        
        if 'page_analyses' in result:
            for page_data in result['page_analyses']:
                page_analysis = page_data.get('analysis', {})
                if 'questions_and_responses' in page_analysis:
                    for q in page_analysis['questions_and_responses']:
                        question_text = q.get('question_text', '').lower()
                        selections = q.get('actual_selections', [])
                        
                        if 'rotational shifts' in question_text and selections:
                            preferences['shift_rotation'] = selections[0]
                        elif 'field' in question_text and selections:
                            preferences['field_work'] = selections[0]
                        elif 'extended periods' in question_text and selections:
                            preferences['extended_periods'] = selections[0]
                        elif 'shared housing' in question_text and selections:
                            preferences['shared_housing'] = selections[0]
        
        return preferences
    
    def _apply_manual_overrides(self, result: Dict, overrides: Dict):
        """Apply manual overrides to the result"""
        
        if 'page_analyses' in result:
            for page_data in result['page_analyses']:
                page_analysis = page_data.get('analysis', {})
                if 'questions_and_responses' in page_analysis:
                    for q in page_analysis['questions_and_responses']:
                        # Check if this question has a manual override
                        question_text = q.get('question_text', '').lower()
                        
                        # Apply overrides based on question content
                        if 'red seal' in question_text and 'red_seal' in overrides:
                            q['actual_selections'] = [overrides['red_seal']]
                            q['manual_override'] = True
                        elif 'journeyman' in question_text and 'journeyman_license' in overrides:
                            q['actual_selections'] = [overrides['journeyman_license']]
                            q['manual_override'] = True
    
    def _generate_summary(self, result: Dict) -> str:
        """Generate a human-readable summary of extraction results"""
        
        summary_lines = []
        
        # Add warning if Dayforce detected
        if result.get('dayforce_warning', {}).get('detected'):
            summary_lines.append("⚠️ DAYFORCE QUESTIONNAIRE DETECTED")
            summary_lines.append("Radio button selections require manual verification")
            summary_lines.append("")
        
        # Add successfully extracted information
        profile = result.get('candidate_profile', {})
        
        # Equipment
        equipment = profile.get('equipment_experience', {})
        if equipment.get('brands_worked_with'):
            summary_lines.append(f"✓ Equipment Brands: {', '.join(equipment['brands_worked_with'])}")
        if equipment.get('equipment_types'):
            summary_lines.append(f"✓ Equipment Types: {', '.join(equipment['equipment_types'])}")
        
        # Certifications (with warnings)
        red_seal = profile.get('red_seal')
        if red_seal:
            if red_seal == "REQUIRES MANUAL VERIFICATION":
                summary_lines.append("❓ Red Seal: Manual verification required")
            else:
                summary_lines.append(f"✓ Red Seal: {red_seal}")
        
        journeyman = profile.get('journeyman_license')
        if journeyman:
            if journeyman == "REQUIRES MANUAL VERIFICATION":
                summary_lines.append("❓ Journeyman License: Manual verification required")
            else:
                summary_lines.append(f"✓ Journeyman License: {journeyman}")
        
        # Work preferences
        prefs = profile.get('work_preferences', {})
        if prefs.get('shift_rotation'):
            summary_lines.append(f"✓ Shift Rotation: {prefs['shift_rotation']}")
        
        # Add manual corrections if any
        if result.get('manual_corrections'):
            summary_lines.append("")
            summary_lines.append("📝 Manual Corrections Applied:")
            for key, value in result['manual_corrections'].items():
                summary_lines.append(f"  • {key}: {value}")
        
        return '\n'.join(summary_lines)
    
    def generate_manual_verification_prompt(self, result: Dict) -> str:
        """Generate a prompt for manual verification of radio button questions"""
        
        prompt_lines = [
            "MANUAL VERIFICATION REQUIRED",
            "=" * 40,
            "The following radio button questions could not be reliably detected:",
            ""
        ]
        
        warning = result.get('dayforce_warning', {})
        for i, question in enumerate(warning.get('affected_questions', []), 1):
            prompt_lines.append(f"{i}. {question['question_text']}")
            prompt_lines.append(f"   Options: {', '.join(question['options'])}")
            prompt_lines.append("")
        
        prompt_lines.append("Please provide the selected option for each question.")
        
        return '\n'.join(prompt_lines)