#!/usr/bin/env python3
"""
Show which processors to keep vs delete
"""

import os

processors_dir = '/home/gotime2022/recruitment_ops/catsone/processors'

# Core processors we should KEEP
keep_files = [
    '__init__.py',
    'cats_integration.py',  # Core CATS API
    'vision_questionnaire_analyzer.py',  # Core vision analysis
    'dynamic_extraction_system.py',  # Core extraction logic
    'job_requirements_extractor.py',  # Job parsing
    'intelligent_candidate_processor.py',  # Main processor
    'comprehensive_attachment_processor.py',  # Attachment handling
    'attachment_classifier.py',  # Attachment classification
]

# Everything else should be deleted or consolidated
all_files = os.listdir(processors_dir)
delete_files = [f for f in all_files if f.endswith('.py') and f not in keep_files]

print("FILES TO KEEP (Core functionality):")
print("-" * 50)
for f in keep_files:
    if os.path.exists(os.path.join(processors_dir, f)):
        print(f"✓ {f}")

print("\n\nFILES TO DELETE (Redundant/test files):")
print("-" * 50)
for f in sorted(delete_files):
    print(f"✗ {f}")

print(f"\n\nTOTAL: Keep {len(keep_files)}, Delete {len(delete_files)}")

# Also check test scripts in root
print("\n\nTEST SCRIPTS IN ROOT TO DELETE:")
print("-" * 50)
root_dir = '/home/gotime2022/recruitment_ops'
test_files = [f for f in os.listdir(root_dir) if f.endswith('.py') and f not in ['main.py', 'setup.py']]
for f in sorted(test_files):
    print(f"✗ {f}")