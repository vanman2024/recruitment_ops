#!/usr/bin/env python3
"""Process a specific candidate directly"""

import os
import sys
from dotenv import load_dotenv

# Load environment
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, '.env'))

# Add project to path
sys.path.append(project_root)

# Import the monitor
from scripts.questionnaire_monitor import EnhancedQuestionnaireMonitor

# Create monitor and process specific candidate
monitor = EnhancedQuestionnaireMonitor()

# Create a fake candidate object with the ID
candidate = {
    'id': 398063905,
    'first_name': 'Micheal',
    'last_name': 'Hennigar'
}

print("Processing candidate 398063905 directly...")
result = monitor.process_candidate(candidate)

if result:
    print("✅ Successfully processed!")
else:
    print("❌ Processing failed - check logs")