#!/usr/bin/env python3
"""
AI-powered notes formatter using Claude to organize questionnaire data
"""

import os
import logging
import json
from typing import Dict, Any
import anthropic

logger = logging.getLogger(__name__)

class AINotesFormatter:
    """Use Claude to intelligently format questionnaire data into comprehensive notes"""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def format_questionnaire_notes(self, questionnaire_data: Dict, job_requirements: Dict) -> str:
        """Use AI to format questionnaire data into comprehensive notes"""
        
        try:
            # Extract all the data
            profile = questionnaire_data.get('candidate_profile', {})
            all_responses = profile.get('all_responses', [])
            
            # Create a comprehensive prompt
            prompt = f"""You are an AI creating a dynamic email summary by analyzing job requirements and candidate questionnaire data.

JOB REQUIREMENTS:
- Title: {job_requirements.get('source', {}).get('job_title', 'Unknown')}
- Required Equipment: {job_requirements.get('required_equipment', [])}
- Required Certifications: {job_requirements.get('required_certifications', [])}
- Required Brands: {job_requirements.get('required_brands', [])}
- Preferred Skills: {job_requirements.get('preferred_equipment', [])}
- Role Type: {job_requirements.get('role_type', 'Unknown')}
- Key Focus Areas: {job_requirements.get('highlight_in_notes', [])}

FULL JOB DESCRIPTION:
{job_requirements.get('source', {}).get('description', '')[:1000]}...

CANDIDATE QUESTIONNAIRE DATA:
{json.dumps(all_responses, indent=2)}

YOUR TASK:
1. FIRST: Analyze the job requirements to understand what matters most for this specific role
2. THEN: Extract ALL relevant information from the questionnaire responses
3. FINALLY: Create a dynamic summary that emphasizes the most relevant qualifications

DYNAMIC STRUCTURING RULES:
- Identify the 3-5 most important aspects for this specific job
- Lead with the strongest matches between candidate and job requirements
- Structure sections based on what's most relevant (don't use a fixed template)
- Include all important information but prioritize based on job relevance

CONSTRAINTS:
- Professional email tone that a recruiter would actually send
- NO markdown formatting - plain text only
- Only use information from the questionnaire (don't make assumptions)
- CRITICAL: DO NOT make up ANY information not in the questionnaire data
- NEVER invent dates, times, or specific details that aren't provided
- If availability timing is mentioned, use ONLY what's in the data
- Locations mentioned are where they're WILLING TO WORK, not relocate
- Skip generic compliance items unless specifically relevant to the job
- If they have multiple certifications relevant to the job, emphasize this strongly

DYNAMIC FORMATTING:
Start with: "Here's a strong candidate for the {job_requirements.get('source', {}).get('job_title', 'position')}:"

Then let the job requirements guide your structure. Examples:
- If equipment is critical → Lead with equipment experience
- If certifications are required → Highlight certifications early
- If location is important → Emphasize their flexibility/availability
- If experience level matters → Focus on years and depth of experience

Create a summary that would make a hiring manager want to interview this candidate by highlighting the best matches with the job requirements.

FINAL REMINDER: 
- Use ONLY information that appears in the questionnaire data above
- Do NOT add any dates, numbers, or specifics not found in the data
- If dates appear in raw format (like 07-10-25), either format them properly or omit them
- If something isn't mentioned in the questionnaire, don't include it
- Be accurate and factual - this is a professional document
- Focus on qualifications and experience, not scheduling details"""

            # Try Claude 4 Opus first
            try:
                response = self.client.messages.create(
                    model="claude-opus-4-20250514",
                    max_tokens=4000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                logger.info("Successfully used Claude 4 Opus for formatting")
            except Exception as opus_error:
                logger.warning(f"Claude 4 Opus failed: {opus_error}, falling back to Claude 4 Sonnet")
                # Fallback to Claude 4 Sonnet
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
            
            formatted_notes = response.content[0].text
            
            # Add equipment summary at the end if needed
            equipment_exp = profile.get('equipment_experience', {})
            if equipment_exp.get('brands_worked_with'):
                formatted_notes += f"\n\nEquipment Summary:\n"
                formatted_notes += f"Brands worked with: {', '.join(equipment_exp['brands_worked_with'])}\n"
            
            return formatted_notes
            
        except Exception as e:
            logger.error(f"Error formatting with AI: {e}")
            # Fallback to basic formatting
            return self._basic_format_fallback(questionnaire_data)
    
    def _basic_format_fallback(self, questionnaire_data: Dict) -> str:
        """Basic fallback formatting if AI fails"""
        
        profile = questionnaire_data.get('candidate_profile', {})
        all_responses = profile.get('all_responses', [])
        
        notes = []
        notes.append("QUESTIONNAIRE RESPONSES")
        notes.append("=" * 50)
        notes.append(f"\nTotal responses: {len(all_responses)}")
        notes.append(f"Red Seal: {profile.get('red_seal', 'Not specified')}")
        notes.append(f"Journeyman: {profile.get('journeyman_license', 'Not specified')}")
        
        # Group responses by category
        for i, response in enumerate(all_responses):
            notes.append(f"\nQ{i+1}: {response.get('question_text', 'Unknown question')}")
            notes.append(f"Answer: {', '.join(response.get('actual_selections', []))}")
        
        return "\n".join(notes)