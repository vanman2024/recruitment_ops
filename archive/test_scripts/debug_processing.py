#!/usr/bin/env python3
"""
Debug the processing error
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Load environment
load_dotenv('/home/gotime2022/recruitment_ops/.env')

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

def test_processing():
    """Test processing with detailed error info"""
    
    print("Starting debug test...")
    print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")
    print(f"CATS_API_KEY: {os.getenv('CATS_API_KEY')[:20]}...")
    
    try:
        processor = IntelligentCandidateProcessor()
        result = processor.process_candidate_for_job(409281807, 16702578)
        
        print("\nResult:")
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            print(f"Notes length: {len(result.get('notes', ''))}")
            print("\nFirst 500 chars of notes:")
            print(result.get('notes', '')[:500])
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"\nException occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_processing()