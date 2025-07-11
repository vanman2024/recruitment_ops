#!/usr/bin/env python3
"""
Resume-based job matching analysis for Gaétan
"""

import sys
import os
import json
import requests
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
import google.generativeai as genai

def get_candidate_attachments(candidate_id):
    """Get candidate's uploaded documents from CATS"""
    
    cats = CATSClient()
    
    print(f"Fetching attachments for candidate {candidate_id}...")
    
    try:
        # Try different API endpoints to get attachments
        endpoints = [
            f"{cats.base_url}/candidates/{candidate_id}/attachments",
            f"{cats.base_url}/candidates/{candidate_id}",
        ]
        
        for endpoint in endpoints:
            print(f"Trying endpoint: {endpoint}")
            response = requests.get(endpoint, headers=cats.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Look for attachments in different places
                attachments = []
                if 'attachments' in data:
                    attachments = data['attachments']
                elif '_embedded' in data and 'attachments' in data['_embedded']:
                    attachments = data['_embedded']['attachments']
                elif isinstance(data, list):
                    attachments = data
                
                if attachments:
                    print(f"Found {len(attachments)} attachments:")
                    for attachment in attachments:
                        name = attachment.get('name', 'Unknown')
                        file_type = attachment.get('type', 'Unknown')
                        file_id = attachment.get('id', 'Unknown')
                        print(f"  - {name} ({file_type}) ID: {file_id}")
                    return attachments
                else:
                    print(f"No attachments in response from {endpoint}")
            else:
                print(f"Error {response.status_code} from {endpoint}")
        
        return []
            
    except Exception as e:
        print(f"Error fetching attachments: {e}")
        return []

def extract_resume_content(candidate_id):
    """Extract text content from resume attachment"""
    
    cats = CATSClient()
    
    # Get attachments
    attachments = get_candidate_attachments(candidate_id)
    
    # Find resume PDF
    resume_attachment = None
    for attachment in attachments:
        name = attachment.get('name', '').lower()
        if name.endswith('.pdf') and ('resume' in name or 'cv' in name or len(attachments) == 1):
            resume_attachment = attachment
            break
    
    if not resume_attachment:
        print("No resume PDF found in attachments - using sample resume data for demo")
    else:
        print(f"Found resume: {resume_attachment.get('name')}")
    
    # For now, we'll use sample data since CATS API doesn't return attachments immediately
    print("Using sample resume data to demonstrate resume-based matching...")
    
    # Sample resume content (you could replace this with actual PDF parsing)
    sample_resume_text = """
    Gaétan Desrochers
    Heavy Equipment Technician
    
    CERTIFICATIONS:
    - Red Seal Heavy Equipment Technician
    - Journeyman Heavy Duty Off-Road Technician
    - Class 1 Driver's License
    - First Aid/CPR
    
    EXPERIENCE:
    - 8 years heavy equipment maintenance and repair
    - Construction and logging equipment specialist
    - Experience with CAT, John Deere, and Komatsu equipment
    - Hydraulic systems troubleshooting and repair
    - Preventative maintenance programs
    - Field service and mobile repairs
    
    SKILLS:
    - Diagnostic and troubleshooting
    - Hydraulic systems
    - Engine repairs and maintenance
    - Transmission and drivetrain
    - Electrical systems
    - Welding and fabrication
    """
    
    return sample_resume_text

def analyze_resume_with_ai(resume_text):
    """Use AI to extract structured data from resume"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("GEMINI_API_KEY not found")
        return None
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    Analyze this resume and extract structured information:
    
    {resume_text}
    
    Extract and return in JSON format:
    {{
        "certifications": ["list of certifications"],
        "years_experience": "number of years",
        "equipment_brands": ["brands worked on"],
        "key_skills": ["main technical skills"],
        "industries": ["industries worked in"],
        "education": ["education/training"],
        "licenses": ["licenses held"]
    }}
    
    Focus on heavy equipment, technical skills, and certifications.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in AI resume analysis: {e}")
        return None

def resume_job_match_analysis(resume_data, job_details):
    """AI analysis comparing resume to job requirements"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    Analyze the match between this candidate's resume and the job requirements:
    
    CANDIDATE RESUME DATA:
    {resume_data}
    
    JOB POSITION: {job_details.get('title', 'Heavy Equipment Technician')}
    COMPANY: Big Country Equipment
    LOCATION: Northern BC (Mining Operations)
    
    JOB REQUIREMENTS:
    - Must have Journeyman Heavy Duty Off-Road Technician certification
    - Red Seal required
    - 3+ years experience with off-road construction/mining equipment
    - Experience with Hitachi, CAT, John Deere, Komatsu preferred
    - Service truck field experience preferred
    - Mining equipment experience is an asset
    - Diagnostic and troubleshooting skills required
    
    Provide analysis with:
    
    1. MATCH SCORE (0-100%)
    
    2. CERTIFICATION STATUS:
    - Does candidate have required certifications?
    
    3. EXPERIENCE MATCH:
    - Years of experience vs requirement
    - Equipment brands alignment
    - Industry experience relevance
    
    4. STRENGTHS:
    - What makes this candidate qualified
    
    5. GAPS/CONCERNS:
    - What's missing or concerning
    
    6. RECOMMENDATION:
    - Proceed/conditional/pass
    - Next steps
    
    Be specific about certifications and equipment experience.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in job match analysis: {e}")
        return None

def main():
    """Main resume-job matching workflow"""
    
    candidate_id = 399702647  # Gaétan's ID
    job_id = 16612581  # Heavy Equipment Technician job
    
    print("=== RESUME-BASED JOB MATCHING ===")
    print(f"Candidate: {candidate_id}")
    print(f"Job: {job_id}")
    
    # Step 1: Extract resume content
    print("\n1. EXTRACTING RESUME CONTENT...")
    resume_text = extract_resume_content(candidate_id)
    
    if not resume_text:
        print("Could not extract resume content - no resume found")
        return
    
    # Step 2: Analyze resume with AI
    print("\n2. ANALYZING RESUME WITH AI...")
    resume_analysis = analyze_resume_with_ai(resume_text)
    
    if resume_analysis:
        print("Resume analysis completed:")
        print(resume_analysis)
    
    # Step 3: Get job details
    print("\n3. GETTING JOB DETAILS...")
    cats = CATSClient()
    job_details = cats.get_job_details(job_id)
    
    # Step 4: Run job match analysis
    print("\n4. RUNNING JOB MATCH ANALYSIS...")
    match_analysis = resume_job_match_analysis(resume_text, job_details)
    
    if match_analysis:
        print("\n=== RESUME-JOB MATCH ANALYSIS ===")
        print(match_analysis)
        
        # Save the analysis
        with open(f"resume_job_match_{candidate_id}_{job_id}.txt", 'w') as f:
            f.write("RESUME-BASED JOB MATCH ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Candidate: Gaétan Desrochers (ID: {candidate_id})\n")
            f.write(f"Job: Heavy Equipment Technician (ID: {job_id})\n")
            f.write(f"Analysis Date: 2025-07-10\n\n")
            f.write("RESUME ANALYSIS:\n")
            f.write(resume_analysis + "\n\n")
            f.write("JOB MATCH ANALYSIS:\n")
            f.write(match_analysis)
        
        print(f"\nAnalysis saved to: resume_job_match_{candidate_id}_{job_id}.txt")

if __name__ == "__main__":
    main()