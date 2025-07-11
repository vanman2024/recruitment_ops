#!/usr/bin/env python3
"""
View what's on page 5 of the questionnaire
"""

import sys
import os
sys.path.append('/home/gotime2022/recruitment_ops')
import google.generativeai as genai
from PIL import Image

def view_page_5():
    """Analyze page 5 to see equipment brands"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    image_path = '/home/gotime2022/recruitment_ops/questionnaire_images/page_5.png'
    image = Image.open(image_path)
    
    prompt = """
    This is page 5 of a heavy equipment technician questionnaire. 
    
    Please identify:
    1. What equipment brands are listed as checkboxes?
    2. Which checkboxes are checked/selected (look for ✓ or X or filled boxes)?
    3. Are there text fields where years of experience are written?
    4. What are the exact years written for each equipment type?
    
    BE VERY SPECIFIC about what is checked vs unchecked.
    List EVERYTHING you see.
    """
    
    response = model.generate_content([prompt, image])
    print("PAGE 5 ANALYSIS:")
    print("=" * 70)
    print(response.text)

if __name__ == "__main__":
    view_page_5()