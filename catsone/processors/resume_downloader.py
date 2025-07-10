#!/usr/bin/env python3
"""
Extract and analyze Gaétan's actual resume from CATS
"""

import sys
import os
import requests
import tempfile
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
import google.generativeai as genai

def get_resume_attachment(candidate_id):
    """Get resume attachment info from CATS"""
    
    cats = CATSClient()
    
    try:
        # Get attachments for candidate
        url = f"{cats.base_url}/candidates/{candidate_id}/attachments"
        response = requests.get(url, headers=cats.headers)
        
        if response.status_code == 200:
            data = response.json()
            attachments = data.get('_embedded', {}).get('attachments', [])
            
            # Find the resume
            for attachment in attachments:
                if attachment.get('is_resume', False):
                    print(f"Found resume: {attachment.get('filename')}")
                    print(f"Attachment ID: {attachment.get('id')}")
                    return attachment
            
            print("No resume found in attachments")
            return None
        else:
            print(f"Error getting attachments: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def download_resume_pdf(attachment_id):
    """Download the resume PDF from CATS"""
    
    cats = CATSClient()
    
    try:
        # Download the attachment
        download_url = f"{cats.base_url}/attachments/{attachment_id}/download"
        print(f"Downloading from: {download_url}")
        
        response = requests.get(download_url, headers=cats.headers)
        
        if response.status_code == 200:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            print(f"Downloaded resume to: {temp_file_path}")
            print(f"File size: {len(response.content)} bytes")
            return temp_file_path
        else:
            print(f"Download failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Download error: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF"""
    
    try:
        import fitz  # PyMuPDF
        
        print(f"Extracting text from: {pdf_path}")
        
        # Open PDF
        doc = fitz.open(pdf_path)
        text = ""
        page_count = doc.page_count
        
        # Extract text from all pages
        for page_num in range(page_count):
            page = doc[page_num]
            page_text = page.get_text()
            text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        doc.close()
        
        print(f"Extracted {len(text)} characters from {page_count} pages")
        return text
        
    except ImportError:
        print("PyMuPDF not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "PyMuPDF"])
        # Re-import after installation
        import fitz
        return extract_text_from_pdf(pdf_path)
        
    except Exception as e:
        print(f"Text extraction error: {e}")
        # Try alternative approach
        try:
            import fitz
            with open(pdf_path, 'rb') as file:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                text = ""
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    text += f"\n--- Page {page_num + 1} ---\n{page.get_text()}"
                doc.close()
                return text
        except Exception as e2:
            print(f"Alternative extraction also failed: {e2}")
            return None

def analyze_resume_with_ai(resume_text, job_details):
    """Analyze resume against job requirements with AI"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("GEMINI_API_KEY not found")
        return None
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    Analyze this resume against the Heavy Equipment Technician job requirements:
    
    RESUME TEXT:
    {resume_text}
    
    JOB REQUIREMENTS:
    - Position: Heavy Equipment Technician (Big Country Equipment)
    - Location: Northern BC mining operations
    - Required: Journeyman Heavy Duty Off-Road Technician certification
    - Required: Red Seal certification
    - Required: 3+ years experience with off-road construction/mining equipment
    - Preferred: Experience with Hitachi, CAT, John Deere, Komatsu
    - Preferred: Service truck field experience
    - Required: Diagnostic and troubleshooting skills
    - Pay: $62.50/hr base, $93.75/hr OT, 14x14 rotation
    
    Provide detailed analysis:
    
    1. CERTIFICATIONS STATUS:
    - Does candidate have Journeyman Heavy Duty Off-Road certification?
    - Does candidate have Red Seal certification?
    - What other certifications are listed?
    
    2. EXPERIENCE ANALYSIS:
    - Years of heavy equipment experience
    - Types of equipment worked on
    - Equipment brands mentioned (CAT, Komatsu, John Deere, etc.)
    - Industries worked in
    - Field service experience
    
    3. SKILLS ASSESSMENT:
    - Diagnostic and troubleshooting abilities
    - Hydraulic systems experience
    - Electrical systems knowledge
    - Maintenance and repair skills
    
    4. MATCH SCORE (0-100%):
    - Overall qualification level for this specific job
    
    5. STRENGTHS:
    - What makes this candidate qualified
    
    6. GAPS/CONCERNS:
    - What's missing or concerning
    
    7. RECOMMENDATION:
    - Should we proceed with this candidate?
    - What additional information is needed?
    - Interview focus areas
    
    Be specific about certifications and equipment brands mentioned.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI analysis error: {e}")
        return None

def main():
    """Main workflow - extract and analyze real resume"""
    
    candidate_id = 399702647
    
    print("=== REAL RESUME ANALYSIS ===")
    print(f"Analyzing candidate: {candidate_id}")
    
    # Step 1: Get resume attachment info
    print("\n1. Getting resume attachment info...")
    attachment = get_resume_attachment(candidate_id)
    
    if not attachment:
        print("No resume found. Cannot proceed.")
        return
    
    attachment_id = attachment.get('id')
    filename = attachment.get('filename')
    
    # Step 2: Download the PDF
    print(f"\n2. Downloading resume PDF...")
    pdf_path = download_resume_pdf(attachment_id)
    
    if not pdf_path:
        print("Could not download resume. Cannot proceed.")
        return
    
    # Step 3: Extract text from PDF
    print(f"\n3. Extracting text from PDF...")
    resume_text = extract_text_from_pdf(pdf_path)
    
    if not resume_text:
        print("Could not extract text from PDF.")
        return
    
    print("\nExtracted resume text:")
    print("-" * 50)
    print(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
    print("-" * 50)
    
    # Step 4: Get job details
    print(f"\n4. Getting job requirements...")
    cats = CATSClient()
    job_details = cats.get_job_details(16612581)  # Heavy Equipment Technician
    
    # Step 5: Run AI analysis
    print(f"\n5. Running AI job match analysis...")
    analysis = analyze_resume_with_ai(resume_text, job_details)
    
    if analysis:
        print("\n=== AI RESUME ANALYSIS ===")
        print(analysis)
        
        # Save analysis
        output_file = f"real_resume_analysis_{candidate_id}.txt"
        with open(output_file, 'w') as f:
            f.write("REAL RESUME ANALYSIS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Candidate: Gaétan Desrochers (ID: {candidate_id})\n")
            f.write(f"Resume File: {filename}\n")
            f.write(f"Analysis Date: 2025-07-10\n\n")
            f.write("EXTRACTED RESUME TEXT:\n")
            f.write("-" * 30 + "\n")
            f.write(resume_text + "\n\n")
            f.write("AI ANALYSIS:\n")
            f.write("-" * 30 + "\n")
            f.write(analysis)
        
        print(f"\nComplete analysis saved to: {output_file}")
    else:
        print("AI analysis failed")
    
    # Clean up temp file
    try:
        os.unlink(pdf_path)
        print(f"Cleaned up temp file: {pdf_path}")
    except:
        pass

if __name__ == "__main__":
    main()