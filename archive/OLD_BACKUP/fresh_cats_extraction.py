#!/usr/bin/env python3
"""
Fresh extraction directly from CATS attachments
"""

import sys
import os
import logging
import requests
import tempfile
import shutil
from datetime import datetime

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
from catsone.processors.dynamic_extraction_system import DynamicExtractionSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_cats_attachments(candidate_id):
    """Check what attachments are in CATS"""
    
    cats = CATSClient()
    
    print("\n📎 CHECKING CATS ATTACHMENTS...")
    print("-" * 70)
    
    try:
        url = f"{cats.base_url}/candidates/{candidate_id}/attachments"
        response = requests.get(url, headers=cats.headers)
        
        if response.status_code == 200:
            data = response.json()
            attachments = data.get('_embedded', {}).get('attachments', [])
            
            print(f"Found {len(attachments)} attachments:")
            for i, att in enumerate(attachments):
                print(f"\n{i+1}. {att.get('filename')}")
                print(f"   ID: {att.get('id')}")
                print(f"   Type: {'Resume' if att.get('is_resume') else 'Other'}")
                print(f"   Created: {att.get('created_at', 'Unknown')}")
                
            return attachments
        else:
            print(f"Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error checking attachments: {e}")
        return []

def download_questionnaire_pages(attachments, candidate_id):
    """Download questionnaire pages from CATS"""
    
    cats = CATSClient()
    temp_dir = tempfile.mkdtemp()
    
    print(f"\n📥 DOWNLOADING QUESTIONNAIRE PAGES TO: {temp_dir}")
    print("-" * 70)
    
    questionnaire_files = []
    page_number = 1
    
    for att in attachments:
        filename = att.get('filename', '').lower()
        
        # Look for questionnaire files
        if any(term in filename for term in ['questionnaire', 'form', 'page', 'assessment', 'recruiting', 'dayforce']):
            print(f"\nDownloading: {att.get('filename')}")
            
            try:
                # Download attachment
                url = f"{cats.base_url}/attachments/{att['id']}/download"
                response = requests.get(url, headers=cats.headers)
                
                if response.status_code == 200:
                    # Save with proper naming
                    if 'page' in filename:
                        # Try to extract page number
                        import re
                        match = re.search(r'page[_\s]*(\d+)', filename)
                        if match:
                            page_num = match.group(1)
                            save_name = f"page_{page_num}.png"
                        else:
                            save_name = f"page_{page_number}.png"
                            page_number += 1
                    else:
                        save_name = f"questionnaire_{page_number}.png"
                        page_number += 1
                    
                    save_path = os.path.join(temp_dir, save_name)
                    
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"   ✓ Saved as: {save_name} ({len(response.content):,} bytes)")
                    questionnaire_files.append(save_path)
                    
                else:
                    print(f"   ✗ Download failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ✗ Error: {e}")
    
    return temp_dir, questionnaire_files

def run_fresh_extraction(candidate_id, job_id):
    """Run extraction on fresh CATS data"""
    
    print("\n" + "=" * 70)
    print("🔄 FRESH EXTRACTION FROM CATS")
    print("=" * 70)
    print(f"Candidate ID: {candidate_id}")
    print(f"Job ID: {job_id}")
    print(f"Timestamp: {datetime.now()}")
    
    # Step 1: Check attachments
    attachments = check_cats_attachments(candidate_id)
    
    if not attachments:
        print("\n❌ No attachments found in CATS!")
        return
    
    # Step 2: Download questionnaire pages
    temp_dir, questionnaire_files = download_questionnaire_pages(attachments, candidate_id)
    
    if not questionnaire_files:
        print("\n❌ No questionnaire files found!")
        shutil.rmtree(temp_dir)
        return
    
    print(f"\n✓ Downloaded {len(questionnaire_files)} questionnaire files")
    
    # Step 3: Run vision analysis
    print("\n🔍 RUNNING VISION ANALYSIS...")
    print("-" * 70)
    
    try:
        gemini_key = os.getenv('GEMINI_API_KEY')
        analyzer = VisionQuestionnaireAnalyzer(gemini_key)
        
        vision_result = analyzer.analyze_questionnaire_images(temp_dir)
        
        if 'error' in vision_result:
            print(f"❌ Vision analysis failed: {vision_result['error']}")
            return
        
        # Step 4: Extract data
        print("\n📊 EXTRACTING DATA...")
        extractor = DynamicExtractionSystem()
        extracted = extractor.extract_all_questionnaire_data(vision_result)
        
        # Show key findings
        print("\n✅ EXTRACTION RESULTS:")
        print("-" * 70)
        
        # Equipment
        if extracted.get('equipment', {}).get('brands_selected'):
            print(f"Equipment Brands: {', '.join(extracted['equipment']['brands_selected'])}")
        else:
            print("Equipment Brands: None selected")
        
        # Certifications
        certs = extracted.get('certifications', {})
        for cert_name, cert_data in certs.items():
            answer = cert_data.get('answer', 'No response')
            print(f"{cert_name}: {answer}")
        
        # Equipment experience
        if extracted.get('equipment', {}).get('equipment_written'):
            print("\nEquipment Experience:")
            for exp in extracted['equipment']['equipment_written']:
                print(f"  • {exp}")
        
        # Step 5: Process with job requirements
        print("\n📝 PROCESSING WITH JOB REQUIREMENTS...")
        processor = IntelligentCandidateProcessor()
        
        # Get job requirements
        job_data = processor.cats.get_job_details(job_id)
        if job_data:
            job_requirements = processor.job_extractor.extract_job_requirements(job_data)
            
            # Add candidate info
            candidate = processor.cats.get_candidate_details(candidate_id)
            candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}"
            
            extracted['candidate_info'] = {
                'name': candidate_name,
                'location': f"{candidate.get('city', '')}, {candidate.get('state', '')}".strip(', '),
                'candidate_id': candidate_id
            }
            
            # Format notes
            custom_requirements = processor._convert_job_requirements_to_template(job_requirements)
            formatted_notes = extractor.format_for_role(
                all_data=extracted,
                role_type=job_requirements['role_type'],
                custom_requirements=custom_requirements
            )
            
            # Add candidate info
            final_notes = processor._add_candidate_info_to_notes(formatted_notes, extracted['candidate_info'])
            
            print("\n📄 FORMATTED NOTES:")
            print("=" * 70)
            print(final_notes)
            print("=" * 70)
            
            # Update CATS
            print("\n📤 Updating CATS...")
            success = processor.cats.update_candidate_notes(candidate_id, final_notes)
            
            if success:
                print("✅ Successfully updated candidate notes in CATS!")
            else:
                print("❌ Failed to update CATS")
            
            # Save detailed results
            result_file = f"fresh_extraction_{candidate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(result_file, 'w') as f:
                f.write("FRESH EXTRACTION FROM CATS\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Candidate: {candidate_name} (ID: {candidate_id})\n")
                f.write(f"Job: {job_requirements['source']['job_title']} (ID: {job_id})\n")
                f.write(f"Timestamp: {datetime.now()}\n\n")
                
                f.write("VISION ANALYSIS SUMMARY:\n")
                f.write("-" * 30 + "\n")
                if 'candidate_profile' in vision_result:
                    profile = vision_result['candidate_profile']
                    if 'actual_responses' in profile:
                        f.write(f"Questions found: {len(profile['actual_responses'])}\n")
                    if 'equipment_analysis' in vision_result:
                        equip = vision_result['equipment_analysis']
                        f.write(f"Equipment brands available: {equip.get('brands_available', [])}\n")
                        f.write(f"Equipment brands selected: {equip.get('brands_selected', [])}\n")
                
                f.write("\n\nFINAL NOTES:\n")
                f.write("-" * 30 + "\n")
                f.write(final_notes)
            
            print(f"\n💾 Detailed results saved to: {result_file}")
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temporary files")

def main():
    """Main entry point"""
    
    # Gaétan's IDs
    candidate_id = 399702647
    job_id = 16612581  # Heavy Equipment Technician
    
    run_fresh_extraction(candidate_id, job_id)

if __name__ == "__main__":
    main()