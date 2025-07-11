#!/usr/bin/env python3
"""
Trigger processing for a candidate
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.intelligent_candidate_processor import IntelligentCandidateProcessor

# Process the candidate
processor = IntelligentCandidateProcessor()
result = processor.process_candidate_for_job(409281807, 16702578)

if result.get('success'):
    print("✅ Processing successful!")
    print(f"\nNotes preview (first 500 chars):")
    print(result['notes'][:500] + "...")
    print(f"\nFull notes length: {len(result['notes'])} characters")
else:
    print(f"❌ Failed: {result.get('error')}")