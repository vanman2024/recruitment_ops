#!/usr/bin/env python3
"""
CATS Notes Updater
Sends formatted questionnaire analysis back to CATS candidate notes
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CATSNotesUpdater:
    """Update CATS candidate notes with formatted analysis results"""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.headers = {
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        }
    
    def format_questionnaire_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """Format vision analysis results for CATS notes"""
        
        candidate_profile = analysis_result.get('candidate_profile', {})
        candidate_info = candidate_profile.get('candidate_info', {})
        actual_responses = candidate_profile.get('actual_responses', {})
        summary = candidate_profile.get('response_summary', {})
        
        # Build formatted notes
        notes = []
        notes.append("AI QUESTIONNAIRE ANALYSIS")
        notes.append("=" * 40)
        notes.append("")
        
        # Candidate basic info
        candidate_name = candidate_info.get('name', 'Unknown')
        analysis_time = analysis_result.get('analysis_timestamp', datetime.now().isoformat())
        notes.append(f"**Candidate:** {candidate_name}")
        notes.append(f"**Analyzed:** {analysis_time[:19].replace('T', ' ')}")
        notes.append("")
        
        # Key qualifications summary
        if summary.get('key_qualifications'):
            notes.append("**KEY QUALIFICATIONS:**")
            for qual in summary['key_qualifications']:
                notes.append(f"  • {qual}")
            notes.append("")
        
        # Experience highlights
        if summary.get('experience_highlights'):
            notes.append("**EXPERIENCE HIGHLIGHTS:**")
            for exp in summary['experience_highlights']:
                notes.append(f"  • {exp}")
            notes.append("")
        
        # Work preferences
        if summary.get('work_preferences'):
            notes.append("**WORK PREFERENCES:**")
            for pref in summary['work_preferences']:
                notes.append(f"  • {pref}")
            notes.append("")
        
        # Potential concerns
        if summary.get('potential_concerns'):
            notes.append("**POTENTIAL CONCERNS:**")
            for concern in summary['potential_concerns']:
                notes.append(f"  • {concern}")
            notes.append("")
        
        # Detailed responses (key ones only)
        notes.append("**DETAILED RESPONSES:**")
        notes.append("-" * 25)
        
        # Industries worked
        for key, response in actual_responses.items():
            if 'industries_worked' in key:
                selections = response.get('selections', [])
                text = response.get('text', [])
                if selections:
                    notes.append(f"**Industries:** {', '.join(selections)}")
                    if text:
                        notes.append(f"  Details: {', '.join(text)}")
        
        # Employment status and availability
        for key, response in actual_responses.items():
            if 'employment_status' in key:
                selections = response.get('selections', [])
                if selections:
                    notes.append(f"**Employment Status:** {', '.join(selections)}")
            
            elif 'start_availability' in key:
                selections = response.get('selections', [])
                if selections:
                    notes.append(f"**Available to Start:** {', '.join(selections)}")
            
            elif 'reason_for_looking' in key:
                selections = response.get('selections', [])
                if selections:
                    notes.append(f"**Reason for Change:** {', '.join(selections)}")
        
        # Technical qualifications
        for key, response in actual_responses.items():
            if any(tech in key for tech in ['red_seal', 'journeyman', 'mining_experience']):
                question = response.get('question', '')[:50] + "..."
                selections = response.get('selections', [])
                if selections:
                    notes.append(f"**{question}:** {', '.join(selections)}")
        
        notes.append("")
        notes.append("**Analysis Method:** Gemini Vision AI")
        notes.append("**Status:** Automatically Generated")
        
        return "\n".join(notes)
    
    def send_notes_to_cats(self, candidate_id: int, formatted_notes: str) -> Dict[str, Any]:
        """Send formatted notes to CATS candidate record"""
        
        try:
            # CATS API endpoint for adding notes
            url = f"{self.api_url}/candidates/{candidate_id}/notes"
            
            payload = {
                "note": formatted_notes,
                "note_type": "general",
                "created_by": "AI Analysis System",
                "created_at": datetime.now().isoformat()
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully added notes to candidate {candidate_id}")
                return {
                    'success': True,
                    'candidate_id': candidate_id,
                    'note_id': response.json().get('id'),
                    'message': 'Notes added successfully'
                }
            else:
                logger.error(f"Failed to add notes: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"CATS API error: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error sending notes to CATS: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_candidate_with_analysis(self, candidate_id: int, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Complete workflow: format analysis and send to CATS"""
        
        try:
            # Format the analysis
            formatted_notes = self.format_questionnaire_analysis(analysis_result)
            
            # Send to CATS
            result = self.send_notes_to_cats(candidate_id, formatted_notes)
            
            # Add formatted notes to result for reference
            result['formatted_notes'] = formatted_notes
            
            return result
            
        except Exception as e:
            logger.error(f"Error in complete update workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Test the notes updater
if __name__ == "__main__":
    import json
    
    # Get API credentials
    api_key = os.getenv('CATS_API_KEY')
    api_url = os.getenv('CATS_API_URL')
    
    if not api_key or not api_url:
        print("CATS API credentials not found in environment")
        exit(1)
    
    # Create updater
    updater = CATSNotesUpdater(api_key, api_url)
    
    # Sample analysis result (from our vision analysis)
    sample_analysis = {
        'candidate_profile': {
            'candidate_info': {'name': 'Gaétan Desrochers'},
            'actual_responses': {
                'q1_industries_worked': {
                    'question': 'What are the main industries you have worked in?',
                    'selections': ['Construction', 'Other'],
                    'text': ['Logging']
                },
                'q2_fast_paced_comfort': {
                    'question': 'Are you comfortable working in a fast-paced environment?',
                    'selections': ['Yes']
                },
                'q6_reason_for_looking': {
                    'question': 'Why are you looking for a new opportunity?',
                    'selections': ['Work-Life Balance']
                }
            },
            'response_summary': {
                'key_qualifications': ['Red Seal Certified'],
                'experience_highlights': ['Industries: Construction, Other', 'Has mining experience'],
                'work_preferences': ['Interested positions: Heavy Equipment Technician', 'Reason for change: Work-Life Balance'],
                'potential_concerns': ['No underground machinery brand experience']
            }
        },
        'analysis_timestamp': datetime.now().isoformat(),
        'method': 'gemini_vision'
    }
    
    # Format and display the notes
    formatted = updater.format_questionnaire_analysis(sample_analysis)
    print("=== FORMATTED NOTES FOR CATS ===")
    print(formatted)
    print("\n=== PREVIEW COMPLETE ===")
    
    # Note: Uncomment below to actually send to CATS
    # candidate_id = 12345  # Replace with actual candidate ID
    # result = updater.update_candidate_with_analysis(candidate_id, sample_analysis)
    # print(f"Update result: {result}")