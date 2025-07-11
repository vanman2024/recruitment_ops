#!/usr/bin/env python3
"""
View what's on page 4 of the questionnaire
"""

import sys
import os
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.processors.vision_questionnaire_analyzer import VisionQuestionnaireAnalyzer
import google.generativeai as genai
from PIL import Image

def view_page_4():
    """Analyze just page 4 to see equipment brands"""
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    image_path = '/home/gotime2022/recruitment_ops/questionnaire_images/page_4.png'
    image = Image.open(image_path)
    
    prompt = """
    This is page 4 of a questionnaire. 
    
    Please identify:
    1. What equipment brands are listed as checkboxes?
    2. Which ones are checked/selected?
    3. Are there text fields for years of experience?
    4. What specific equipment types are mentioned?
    
    List EVERYTHING you see related to equipment brands and types.
    """
    
    response = model.generate_content([prompt, image])
    print("PAGE 4 ANALYSIS:")
    print("=" * 70)
    print(response.text)

if __name__ == "__main__":
    view_page_4()