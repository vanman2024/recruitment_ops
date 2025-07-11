#!/usr/bin/env python3
"""
Verify checkbox detection accuracy - need 100% accuracy for hiring managers
"""

import os
import sys
sys.path.append('/home/gotime2022/recruitment_ops')
import google.generativeai as genai
from PIL import Image

def verify_specific_question(page_number, question_text):
    """Check a specific question to verify what's actually selected"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    image_path = f'/home/gotime2022/recruitment_ops/questionnaire_images/page_{page_number}.png'
    image = Image.open(image_path)
    
    # Very specific prompt to verify selections
    prompt = f"""
    Look at this questionnaire page VERY CAREFULLY.
    
    Find the question about: "{question_text}"
    
    Tell me EXACTLY what you see:
    1. Is there a checkbox, radio button, or other selection mechanism?
    2. What visual indicator shows if it's selected? (checkmark ✓, X, filled circle ●, empty circle ○, etc.)
    3. For THIS specific question, what is the ACTUAL visual state you see?
    4. List each option and whether it has a mark or not
    
    BE EXTREMELY PRECISE. Look for:
    - Checkmarks (✓)
    - X marks
    - Filled circles (●) vs empty circles (○)
    - Filled squares vs empty squares
    - Any other marking
    
    DO NOT GUESS. Only report what you literally see.
    """
    
    response = model.generate_content([prompt, image])
    return response.text

# Check the underground mechanic question
print("VERIFYING: Underground mechanic experience question")
print("=" * 60)

# Need to find which page has this question
for page in range(1, 7):
    print(f"\nChecking page {page}...")
    result = verify_specific_question(page, "underground mechanic")
    if "underground" in result.lower() and "mechanic" in result.lower():
        print(f"\nFOUND ON PAGE {page}:")
        print(result)
        break

print("\n\nVERIFYING: Red Seal question")
print("=" * 60)

for page in range(1, 7):
    result = verify_specific_question(page, "Red Seal")
    if "red seal" in result.lower():
        print(f"\nFOUND ON PAGE {page}:")
        print(result)
        break