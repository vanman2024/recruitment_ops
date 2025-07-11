#!/usr/bin/env python3
"""
Analyze what selections are being captured
"""

import json

with open('extraction_debug.json', 'r') as f:
    data = json.load(f)

print("QUESTIONS WITH ACTUAL SELECTIONS:")
print("=" * 70)

found_any = False
for page in data['vision_result']['page_analyses']:
    page_name = page['page']
    for q in page['analysis']['questions_and_responses']:
        if q.get('actual_selections') and len(q['actual_selections']) > 0:
            found_any = True
            print(f"\nPage: {page_name}")
            print(f"Question: {q['question_text']}")
            print(f"Selections: {q['actual_selections']}")

if not found_any:
    print("\nNO QUESTIONS HAD ACTUAL SELECTIONS CAPTURED!")
    
print("\n\nQUESTIONS THAT SHOULD HAVE SELECTIONS:")
print("=" * 70)

# Check specific questions
important_questions = [
    "Do you have your Red Seal?",
    "Do you have a Valid Journeyman Off-Road License?",
    "Which of the following underground machinery brands"
]

for page in data['vision_result']['page_analyses']:
    page_name = page['page']
    for q in page['analysis']['questions_and_responses']:
        for iq in important_questions:
            if iq in q.get('question_text', ''):
                print(f"\nPage: {page_name}")
                print(f"Question: {q['question_text']}")
                print(f"Type: {q.get('question_type')}")
                print(f"Options: {q.get('all_available_options', [])}")
                print(f"Actual Selections: {q.get('actual_selections', [])} <-- EMPTY!" if not q.get('actual_selections') else f"Actual Selections: {q.get('actual_selections', [])}")