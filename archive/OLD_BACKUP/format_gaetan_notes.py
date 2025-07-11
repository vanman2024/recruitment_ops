#!/usr/bin/env python3
"""
Format Gaétan's notes using structured template
"""

import sys
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.structured_note_formatter import format_from_questionnaire
from catsone.integration.cats_integration import CATSClient

# Based on what we know from Gaétan's actual questionnaire
questionnaire_data = {
    'candidate_name': 'Gaétan Desrochers',
    'red_seal': 'YES',  # From your screenshot
    'industries': ['Construction', 'Logging'],
    'current_position': 'Shop Foreman',
    'current_company': 'Mount Sicker Logging',
    'employment_status': 'Employed',
    'reason_for_looking': 'Work-Life Balance',
    'availability': 'Within 1 month',
    'position_interested': 'Journeyman Heavy Equipment Technician',
    'hydraulics_knowledge': 'Intermediate',
    'equipment_brands': ['None of the above'],  # For underground brands
    'equipment_written': '4 years on wheeled loader excavator off road equipment, 3 years on truck, 15 years of logging equipment only',
    'years_experience': '22',  # From service truck response
    'underground_mechanic': 'NO',  # Per the vision analysis
    'komatsu_pc5000': 'NO'
}

# Format the notes
formatted_notes = format_from_questionnaire(
    questionnaire_data,
    recruiter_notes="Strong mechanical background with extensive forestry equipment experience"
)

print("FORMATTED NOTES:")
print("=" * 60)
print(formatted_notes)

# Update CATS
cats = CATSClient()
success = cats.update_candidate_notes(399702647, formatted_notes)

if success:
    print("\n✅ Successfully updated CATS with structured format")
else:
    print("\n❌ Failed to update CATS")