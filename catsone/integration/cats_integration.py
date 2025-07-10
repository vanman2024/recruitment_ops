"""
CATS ATS Integration Module
Handles API communication with CATS for candidate and job management
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging
import sys
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.config import CATS_API_KEY, CATS_API_URL, CATS_COMPANY_ID

logger = logging.getLogger(__name__)


class CATSClient:
    """Client for CATS ATS API v3"""
    
    def __init__(self):
        self.api_key = CATS_API_KEY
        self.base_url = CATS_API_URL
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_job_orders(self, status="open"):
        """Get all job orders/openings"""
        endpoint = f"{self.base_url}/jobs"
        params = {
            "per_page": 100
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching job orders: {e}")
            return None
    
    def get_job_details(self, job_id):
        """Get detailed job requirements"""
        endpoint = f"{self.base_url}/jobs/{job_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return None
    
    def search_candidates(self, query):
        """Search existing candidates"""
        endpoint = f"{self.base_url}/candidates/search"
        params = {"query": query}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
            return None
    
    def create_candidate(self, candidate_data):
        """Create new candidate record"""
        endpoint = f"{self.base_url}/candidates"
        
        # Map our data to CATS format
        cats_data = {
            "first_name": candidate_data.get("first_name"),
            "last_name": candidate_data.get("last_name"),
            "email": candidate_data.get("email"),
            "phone_home": candidate_data.get("phone"),
            "address": candidate_data.get("address"),
            "city": candidate_data.get("city"),
            "state": candidate_data.get("province"),
            "zip": candidate_data.get("postal_code"),
            "key_skills": ", ".join(candidate_data.get("skills", [])),
            "notes": candidate_data.get("summary", "")
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=cats_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating candidate: {e}")
            return None
    
    def add_candidate_to_job(self, candidate_id, job_id, status="New Applicant"):
        """Add candidate to job pipeline"""
        endpoint = f"{self.base_url}/candidates/{candidate_id}/joborders/{job_id}"
        
        data = {
            "status": status,
            "date_submitted": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error adding candidate to job: {e}")
            return None
    
    def create_activity(self, candidate_id, activity_type, notes, job_id=None):
        """Log an activity for a candidate"""
        endpoint = f"{self.base_url}/activities"
        
        data = {
            "candidate_id": candidate_id,
            "type": activity_type,
            "notes": notes,
            "date": datetime.now().isoformat()
        }
        
        if job_id:
            data["joborder_id"] = job_id
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating activity: {e}")
            return None
    
    def upload_resume(self, candidate_id, file_path):
        """Upload resume file to candidate"""
        endpoint = f"{self.base_url}/candidates/{candidate_id}/attachments"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                # Remove Content-Type for multipart upload
                headers = {"Authorization": f"Token {self.api_key}"}
                response = requests.post(endpoint, headers=headers, files=files)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            return None
    
    def get_candidate_details(self, candidate_id):
        """Get full candidate details including custom fields"""
        endpoint = f"{self.base_url}/candidates/{candidate_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching candidate details: {e}")
            return None
    
    def update_candidate_notes(self, candidate_id, notes):
        """Update candidate notes field"""
        endpoint = f"{self.base_url}/candidates/{candidate_id}"
        
        data = {
            "notes": notes
        }
        
        try:
            response = requests.put(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error updating candidate notes: {e}")
            return False
    
    def get_candidate_pipelines(self, candidate_id):
        """Get candidate's pipeline statuses"""
        endpoint = f"{self.base_url}/candidates/{candidate_id}/pipelines"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching candidate pipelines: {e}")
            return None
    
    def update_candidate_custom_field(self, candidate_id, field_id, value):
        """Update a specific custom field for a candidate"""
        endpoint = f"{self.base_url}/candidates/{candidate_id}/custom_fields/{field_id}"
        
        data = {
            "value": value
        }
        
        try:
            response = requests.put(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error updating custom field: {e}")
            return False


class JobMatcher:
    """Match candidates to jobs based on requirements"""
    
    def __init__(self, cats_client: CATSClient):
        self.cats = cats_client
    
    def match_candidate_to_jobs(self, candidate_data, job_list=None):
        """Score candidate against available jobs"""
        
        # Get all open jobs if not provided
        if not job_list:
            jobs_response = self.cats.get_job_orders()
            if not jobs_response:
                return []
            job_list = jobs_response.get("data", [])
        
        matches = []
        
        for job in job_list:
            # Get full job details
            job_details = self.cats.get_job_details(job["id"])
            if not job_details:
                continue
            
            # Calculate match score
            score = self.calculate_match_score(candidate_data, job_details)
            
            matches.append({
                "job_id": job["id"],
                "job_title": job_details.get("title"),
                "company": job_details.get("company_name"),
                "location": job_details.get("city"),
                "match_score": score,
                "matching_skills": score["matching_skills"],
                "missing_skills": score["missing_skills"]
            })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"]["total"], reverse=True)
        
        return matches
    
    def calculate_match_score(self, candidate, job):
        """Calculate how well candidate matches job requirements"""
        
        score = {
            "total": 0,
            "skills_match": 0,
            "experience_match": 0,
            "certification_match": 0,
            "matching_skills": [],
            "missing_skills": []
        }
        
        # Extract job requirements (would need parsing from job description)
        job_requirements = self.parse_job_requirements(job.get("description", ""))
        
        # Match equipment brands
        candidate_brands = candidate.get("summary", {}).get("primary_equipment_brands", [])
        job_brands = job_requirements.get("equipment_brands", [])
        
        brand_matches = set(candidate_brands) & set(job_brands)
        if job_brands:
            score["skills_match"] = len(brand_matches) / len(job_brands) * 40
        
        # Match experience years
        candidate_years = candidate.get("resume_data", {}).get("heavy_equipment_experience", {}).get("total_years", 0)
        required_years = job_requirements.get("min_experience_years", 0)
        
        if candidate_years >= required_years:
            score["experience_match"] = 30
        else:
            score["experience_match"] = (candidate_years / required_years) * 30 if required_years > 0 else 0
        
        # Match certifications
        candidate_certs = self.extract_all_certifications(candidate)
        required_certs = job_requirements.get("certifications", [])
        
        cert_matches = set(candidate_certs) & set(required_certs)
        if required_certs:
            score["certification_match"] = len(cert_matches) / len(required_certs) * 30
        
        # Calculate total
        score["total"] = score["skills_match"] + score["experience_match"] + score["certification_match"]
        score["matching_skills"] = list(brand_matches) + list(cert_matches)
        score["missing_skills"] = list(set(job_brands) - set(candidate_brands))
        
        return score
    
    def parse_job_requirements(self, job_description):
        """Parse job description for requirements"""
        # This would use NLP or Gemini to extract requirements
        # For now, return sample structure
        return {
            "equipment_brands": ["CAT", "Komatsu"],
            "min_experience_years": 5,
            "certifications": ["Red Seal", "Class 1"],
            "skills": ["mining", "maintenance"]
        }
    
    def extract_all_certifications(self, candidate):
        """Extract all certifications from candidate data"""
        certs = []
        
        # From resume
        resume_certs = candidate.get("resume_data", {}).get("certifications", {})
        certs.extend(resume_certs.get("red_seal", []))
        certs.extend(resume_certs.get("safety", []))
        certs.extend(resume_certs.get("licenses", []))
        
        return certs


# Example usage
if __name__ == "__main__":
    # Initialize CATS client
    cats = CATSClient()
    
    # Test API connection
    jobs = cats.get_job_orders()
    if jobs:
        print(f"Found {len(jobs.get('data', []))} open positions")
    
    # Initialize job matcher
    matcher = JobMatcher(cats)
    
    # Load candidate data (would come from our processing)
    with open("output/jeff_miller_complete_analysis.json", "r") as f:
        candidate_data = json.load(f)
    
    # Find matching jobs
    matches = matcher.match_candidate_to_jobs(candidate_data)
    
    print("\nTop Job Matches:")
    for match in matches[:5]:
        print(f"\n{match['job_title']} - {match['company']}")
        print(f"Match Score: {match['match_score']['total']:.1f}%")
        print(f"Matching Skills: {', '.join(match['matching_skills'])}")