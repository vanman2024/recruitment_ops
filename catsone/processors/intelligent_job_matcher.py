#!/usr/bin/env python3
"""
Intelligent job matching using Gemini 2.5 Pro to analyze job descriptions
and match against candidate profiles
"""

import json
from pathlib import Path
from typing import List, Dict
import logging

from config import GEMINI_MODEL

logger = logging.getLogger(__name__)


class IntelligentJobMatcher:
    """Use Gemini to intelligently match candidates to jobs"""
    
    def __init__(self):
        self.model = GEMINI_MODEL  # gemini-2.5-pro
        
    def analyze_job_requirements(self, job_description: str) -> Dict:
        """Use Gemini to extract structured requirements from job description"""
        
        prompt = f"""
        Analyze this heavy equipment job description and extract structured requirements.
        
        Job Description:
        {job_description}
        
        Extract the following in JSON format:
        {{
            "required_equipment": {{
                "brands": ["list of equipment brands mentioned"],
                "types": ["types of equipment: shovel, drill, dozer, etc"],
                "models": ["specific models if mentioned"]
            }},
            "experience_requirements": {{
                "minimum_years": number,
                "specific_experience": ["specific experience requirements"],
                "industries": ["mining", "construction", "oil & gas", etc]
            }},
            "certifications_required": {{
                "mandatory": ["required certifications"],
                "preferred": ["nice to have certifications"]
            }},
            "skills": {{
                "technical": ["technical skills"],
                "soft": ["soft skills mentioned"]
            }},
            "location": "job location",
            "key_responsibilities": ["main job duties"]
        }}
        
        Be very specific and only include what's explicitly mentioned in the job description.
        """
        
        # This would call Gemini through MCP
        # For now, return structure for demonstration
        return {
            "prompt": prompt,
            "model": self.model,
            "instruction": "Use mcp__gemini__generate_content with this prompt"
        }
    
    def match_candidate_to_job(self, candidate_data: Dict, job_requirements: Dict) -> Dict:
        """Use Gemini to intelligently score candidate against job"""
        
        prompt = f"""
        You are an expert recruiter for heavy equipment operations. Analyze how well this candidate matches the job requirements.
        
        CANDIDATE PROFILE:
        {json.dumps(candidate_data.get("summary", {}), indent=2)}
        
        JOB REQUIREMENTS:
        {json.dumps(job_requirements, indent=2)}
        
        Provide a detailed matching analysis in JSON format:
        {{
            "overall_match_score": 0-100,
            "scoring_breakdown": {{
                "equipment_match": {{
                    "score": 0-100,
                    "matching_items": ["list of matching equipment/brands"],
                    "missing_items": ["required equipment candidate lacks"],
                    "explanation": "brief explanation"
                }},
                "experience_match": {{
                    "score": 0-100,
                    "meets_minimum": true/false,
                    "relevant_experience": ["relevant experience points"],
                    "gaps": ["experience gaps"],
                    "explanation": "brief explanation"
                }},
                "certification_match": {{
                    "score": 0-100,
                    "has_mandatory": ["mandatory certs they have"],
                    "missing_mandatory": ["mandatory certs they lack"],
                    "has_preferred": ["preferred certs they have"],
                    "explanation": "brief explanation"
                }},
                "skills_match": {{
                    "score": 0-100,
                    "matching_skills": ["matching technical/soft skills"],
                    "missing_skills": ["skills they lack"],
                    "transferable_skills": ["skills that could transfer"],
                    "explanation": "brief explanation"
                }}
            }},
            "strengths": ["top 3-5 reasons they're a good fit"],
            "concerns": ["top 3-5 concerns or gaps"],
            "recommendation": "STRONG_MATCH|GOOD_MATCH|POSSIBLE_MATCH|POOR_MATCH",
            "interview_focus_areas": ["suggested interview topics based on gaps"],
            "development_opportunities": ["training/certs that would help"]
        }}
        
        Be objective and detailed in your analysis. Consider both direct matches and transferable skills.
        """
        
        return {
            "prompt": prompt,
            "model": self.model,
            "instruction": "Use mcp__gemini__generate_content with this prompt"
        }
    
    def generate_interview_questions(self, candidate_data: Dict, job_requirements: Dict, match_analysis: Dict) -> List[str]:
        """Generate targeted interview questions based on the match analysis"""
        
        prompt = f"""
        Based on this candidate's profile and job match analysis, generate 10 targeted interview questions.
        
        CANDIDATE SUMMARY:
        {json.dumps(candidate_data.get("summary", {}), indent=2)}
        
        MATCH ANALYSIS CONCERNS:
        {json.dumps(match_analysis.get("concerns", []), indent=2)}
        
        EXPERIENCE GAPS:
        {json.dumps(match_analysis.get("scoring_breakdown", {}).get("experience_match", {}).get("gaps", []), indent=2)}
        
        Generate behavioral and technical interview questions that:
        1. Verify their claimed experience with specific equipment
        2. Explore how they'd handle the gaps identified
        3. Assess problem-solving in equipment operation scenarios
        4. Understand their safety practices and protocols
        5. Evaluate their ability to learn new equipment/systems
        
        Format as a JSON array of questions with purpose:
        [
            {{
                "question": "the interview question",
                "purpose": "what this question assesses",
                "follow_up": "suggested follow-up if needed"
            }}
        ]
        """
        
        return {
            "prompt": prompt,
            "model": self.model,
            "instruction": "Use mcp__gemini__generate_content with this prompt"
        }


def demonstrate_intelligent_matching():
    """Show how intelligent matching would work"""
    
    print("Intelligent Job Matching with Gemini 2.5 Pro")
    print("=" * 60)
    
    # Load candidate data
    try:
        with open("output/jeff_miller_complete_analysis.json", "r") as f:
            candidate_data = json.load(f)
    except:
        print("Candidate data not found. Run analysis first.")
        return
    
    # Sample job description
    sample_job = """
    Heavy Equipment Operator - Surface Mining
    
    We are seeking an experienced Heavy Equipment Operator for our surface mining operations.
    
    Requirements:
    - Minimum 7 years operating heavy equipment in mining environment
    - Experience with CAT 793F/797F haul trucks required
    - Experience with Komatsu PC5500 or similar hydraulic shovels preferred
    - Valid MSHA certification
    - Class 1 driver's license
    - Strong safety record
    
    Responsibilities:
    - Operate haul trucks and shovels in surface mine
    - Perform pre-operational checks
    - Maintain equipment logs
    - Work with dispatch for efficient operations
    
    Location: Fort McMurray, AB
    """
    
    matcher = IntelligentJobMatcher()
    
    print("\n1. Analyzing Job Requirements with Gemini...")
    job_analysis = matcher.analyze_job_requirements(sample_job)
    print(f"   Model: {job_analysis['model']}")
    print("   To execute: mcp__gemini__generate_content with the generated prompt")
    
    print("\n2. Matching Candidate to Job...")
    # Simulate job requirements (would come from Gemini analysis)
    job_requirements = {
        "required_equipment": {
            "brands": ["CAT"],
            "types": ["haul trucks", "hydraulic shovels"],
            "models": ["CAT 793F", "CAT 797F", "Komatsu PC5500"]
        },
        "experience_requirements": {
            "minimum_years": 7,
            "specific_experience": ["surface mining operations"],
            "industries": ["mining"]
        },
        "certifications_required": {
            "mandatory": ["MSHA certification", "Class 1 license"],
            "preferred": []
        },
        "location": "Fort McMurray, AB"
    }
    
    match_analysis = matcher.match_candidate_to_job(candidate_data, job_requirements)
    print("   This would provide detailed scoring and gap analysis")
    
    print("\n3. Generating Interview Questions...")
    # Simulate match analysis results
    mock_match_analysis = {
        "concerns": ["No MSHA certification mentioned", "No specific CAT haul truck experience listed"],
        "scoring_breakdown": {
            "experience_match": {
                "gaps": ["CAT 793F/797F haul truck operation"]
            }
        }
    }
    
    questions = matcher.generate_interview_questions(candidate_data, job_requirements, mock_match_analysis)
    print("   This would generate targeted behavioral and technical questions")
    
    print("\n" + "=" * 60)
    print("With Gemini 2.5 Pro, we can:")
    print("✓ Intelligently parse any job description format")
    print("✓ Understand context and transferable skills")
    print("✓ Generate nuanced match scores beyond keyword matching")
    print("✓ Create targeted interview strategies")
    print("✓ Suggest development paths for candidates")


if __name__ == "__main__":
    demonstrate_intelligent_matching()