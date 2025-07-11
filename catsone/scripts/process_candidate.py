#!/usr/bin/env python3
"""
MAIN CANDIDATE PROCESSING SCRIPT
Processes candidates from CATS with questionnaire analysis
"""

import sys
import os
import logging
from datetime import datetime

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_candidate_from_cats(candidate_id: int, job_id: int):
    """
    Main function to process a candidate from CATS
    
    This will:
    1. Download all attachments from CATS
    2. Classify them (resume, questionnaire, etc)
    3. Process questionnaires with vision analysis
    4. Extract all relevant information
    5. Format notes based on job requirements
    6. Update CATS with the results
    """
    
    print("\n" + "=" * 70)
    print("CANDIDATE PROCESSING")
    print("=" * 70)
    print(f"Candidate ID: {candidate_id}")
    print(f"Job ID: {job_id}")
    print(f"Timestamp: {datetime.now()}")
    
    try:
        # Initialize processor
        processor = IntelligentCandidateProcessor()
        
        # Process candidate
        result = processor.process_candidate_for_job(candidate_id, job_id)
        
        if result.get('success'):
            print(f"\n✅ SUCCESS: Processed {result['candidate_name']} for {result['job_title']}")
            
            print("\n📄 FORMATTED NOTES:")
            print("=" * 70)
            print(result['notes'])
            print("=" * 70)
            
            # Save results
            filename = f"candidate_{candidate_id}_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(f"CANDIDATE PROCESSING RESULTS\n")
                f.write(f"{'=' * 70}\n\n")
                f.write(f"Candidate: {result['candidate_name']} (ID: {candidate_id})\n")
                f.write(f"Job: {result['job_title']} (ID: {job_id})\n")
                f.write(f"Processed: {datetime.now()}\n\n")
                f.write("NOTES:\n")
                f.write("-" * 30 + "\n")
                f.write(result['notes'])
            
            print(f"\n💾 Results saved to: {filename}")
            
        else:
            print(f"\n❌ FAILED: {result.get('error')}")
            
    except Exception as e:
        logging.error(f"Error processing candidate: {e}")
        print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""
    
    # Default to Gaétan for testing
    candidate_id = 399702647
    job_id = 16612581
    
    # Allow command line args
    if len(sys.argv) > 2:
        candidate_id = int(sys.argv[1])
        job_id = int(sys.argv[2])
    
    process_candidate_from_cats(candidate_id, job_id)

if __name__ == "__main__":
    main()