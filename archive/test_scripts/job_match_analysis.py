#!/usr/bin/env python3
"""
AI-powered job matching analysis for Gaétan
"""

import sys
import os
import json
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
import google.generativeai as genai

def get_candidate_job_pipeline(candidate_id):
    """Get jobs that candidate is in pipeline for"""
    
    cats = CATSClient()
    
    print(f"Fetching pipeline information for candidate {candidate_id}...")
    
    # Get candidate pipelines
    pipelines = cats.get_candidate_pipelines(candidate_id)
    
    if pipelines:
        print(f"Found pipeline data:")
        print(json.dumps(pipelines, indent=2))
        return pipelines
    else:
        print("No pipeline data found")
        return None

def get_job_details(job_id):
    """Get detailed job information"""
    
    cats = CATSClient()
    
    print(f"Fetching job details for job ID: {job_id}...")
    
    job_details = cats.get_job_details(job_id)
    
    if job_details:
        print(f"Job Title: {job_details.get('title', 'Unknown')}")
        print(f"Company: {job_details.get('company_name', 'Unknown')}")
        print(f"Location: {job_details.get('city', 'Unknown')}")
        
        # Print job description
        description = job_details.get('description', '')
        if description:
            print(f"\nJob Description:")
            print("-" * 50)
            print(description[:500] + "..." if len(description) > 500 else description)
            print("-" * 50)
        
        return job_details
    else:
        print("Could not fetch job details")
        return None

def ai_job_match_analysis(candidate_data, job_details):
    """Use Gemini AI to analyze candidate-job match"""
    
    # Get Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("GEMINI_API_KEY not found")
        return None
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Prepare candidate summary
    candidate_summary = f"""
    CANDIDATE: {candidate_data.get('name', 'Unknown')}
    
    QUESTIONNAIRE RESPONSES:
    - Industries Worked: Construction, Logging
    - Fast-Paced Environment: Comfortable
    - Employment Status: Currently Employed
    - Availability: Within 1 month
    - Reason for Change: Work-Life Balance
    - Hydraulic Systems: Intermediate level
    - Underground Experience: None
    - Equipment Background: Construction/Logging
    """
    
    # Prepare job summary
    job_summary = f"""
    JOB POSITION: {job_details.get('title', 'Unknown')}
    COMPANY: {job_details.get('company_name', 'Unknown')}
    LOCATION: {job_details.get('city', 'Unknown')}
    
    JOB DESCRIPTION:
    {job_details.get('description', 'No description available')}
    """
    
    # Create analysis prompt
    prompt = f"""
    You are an expert recruitment analyst. Analyze the match between this candidate and job position.
    
    {candidate_summary}
    
    {job_summary}
    
    Provide a comprehensive analysis including:
    
    1. OVERALL MATCH SCORE (0-100%)
    
    2. STRENGTHS (What makes this candidate a good fit):
    - List specific qualifications that match
    - Highlight relevant experience
    
    3. CONCERNS/GAPS (What might be missing or concerning):
    - Identify missing requirements
    - Note potential challenges
    
    4. SPECIFIC RECOMMENDATIONS:
    - What additional information to gather
    - What questions to ask in interview
    - What training might be needed
    
    5. NEXT STEPS:
    - Immediate actions to take
    - How to address any concerns
    
    Be specific and actionable in your analysis. Focus on heavy equipment, mining, and construction industry requirements.
    """
    
    print("Running AI job match analysis...")
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return None

def main():
    """Main job matching workflow"""
    
    candidate_id = 399702647  # Gaétan's ID
    
    print("=== AI JOB MATCHING ANALYSIS ===")
    print(f"Candidate ID: {candidate_id}")
    
    # Step 1: Get candidate's pipeline jobs
    pipelines = get_candidate_job_pipeline(candidate_id)
    
    if not pipelines:
        print("No pipeline data found. Cannot proceed with job matching.")
        return
    
    # Step 2: Extract job IDs from pipeline
    job_ids = []
    if isinstance(pipelines, dict) and '_embedded' in pipelines:
        pipeline_list = pipelines['_embedded'].get('pipelines', [])
        for pipeline in pipeline_list:
            if 'job_id' in pipeline:
                job_ids.append(pipeline['job_id'])
                print(f"Found job ID: {pipeline['job_id']}")
    elif isinstance(pipelines, list):
        for pipeline in pipelines:
            if 'job_id' in pipeline:
                job_ids.append(pipeline['job_id'])
            elif 'joborder_id' in pipeline:
                job_ids.append(pipeline['joborder_id'])
    elif isinstance(pipelines, dict) and 'data' in pipelines:
        for pipeline in pipelines['data']:
            if 'job_id' in pipeline:
                job_ids.append(pipeline['job_id'])
            elif 'joborder_id' in pipeline:
                job_ids.append(pipeline['joborder_id'])
    
    if not job_ids:
        print("No job IDs found in pipeline data")
        return
    
    print(f"Found {len(job_ids)} jobs in pipeline: {job_ids}")
    
    # Step 3: Analyze each job
    for job_id in job_ids[:1]:  # Analyze first job for now
        print(f"\n=== ANALYZING JOB {job_id} ===")
        
        job_details = get_job_details(job_id)
        
        if job_details:
            # Candidate data from questionnaire
            candidate_data = {
                'name': 'Gaétan Desrochers',
                'questionnaire_data': {
                    'industries': ['Construction', 'Logging'],
                    'fast_paced': 'Comfortable',
                    'employment_status': 'Currently Employed',
                    'availability': 'Within 1 month',
                    'reason_for_change': 'Work-Life Balance',
                    'hydraulic_systems': 'Intermediate',
                    'underground_experience': 'None'
                }
            }
            
            # Run AI analysis
            analysis = ai_job_match_analysis(candidate_data, job_details)
            
            if analysis:
                print("\n=== AI MATCH ANALYSIS ===")
                print(analysis)
                
                # Save analysis for CATS notes update
                analysis_file = f"job_match_analysis_{candidate_id}_{job_id}.txt"
                with open(analysis_file, 'w') as f:
                    f.write(f"AI Job Match Analysis\n")
                    f.write(f"Candidate: Gaétan Desrochers (ID: {candidate_id})\n")
                    f.write(f"Job: {job_details.get('title', 'Unknown')} (ID: {job_id})\n")
                    f.write(f"Analysis Date: 2025-07-10\n\n")
                    f.write(analysis)
                
                print(f"\nAnalysis saved to: {analysis_file}")
            else:
                print("AI analysis failed")

if __name__ == "__main__":
    main()