#!/usr/bin/env python3
"""
Check if PDF has form field data
"""

import sys
import os
import requests
import tempfile
sys.path.append('/home/gotime2022/recruitment_ops')
from catsone.integration.cats_integration import CATSClient
import fitz  # PyMuPDF

def check_pdf_form_fields():
    """Check if PDF contains form field data"""
    
    cats = CATSClient()
    
    # Download Dayforce PDF
    url = f"{cats.base_url}/candidates/399702647/attachments"
    response = requests.get(url, headers=cats.headers)
    
    if response.status_code == 200:
        data = response.json()
        attachments = data.get('_embedded', {}).get('attachments', [])
        
        for att in attachments:
            if 'dayforce' in att.get('filename', '').lower():
                # Download it
                download_url = f"{cats.base_url}/attachments/{att['id']}/download"
                pdf_response = requests.get(download_url, headers=cats.headers)
                
                if pdf_response.status_code == 200:
                    # Save PDF
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                        f.write(pdf_response.content)
                        pdf_path = f.name
                    
                    print("PDF FORM FIELD ANALYSIS")
                    print("=" * 70)
                    
                    # Open with PyMuPDF
                    doc = fitz.open(pdf_path)
                    
                    # Check for form fields
                    for page_num in range(doc.page_count):
                        page = doc[page_num]
                        
                        print(f"\nPage {page_num + 1}:")
                        print("-" * 30)
                        
                        # Get widgets (form fields)
                        widgets = page.widgets()
                        field_count = 0
                        
                        for widget in widgets:
                            field_count += 1
                            print(f"\nField {field_count}:")
                            print(f"  Type: {widget.field_type_string}")
                            print(f"  Name: {widget.field_name}")
                            print(f"  Value: {widget.field_value}")
                            print(f"  Text: {widget.field_display}")
                            
                            # For radio/checkbox, check if selected
                            if widget.field_type in [fitz.PDF_WIDGET_TYPE_CHECKBOX, fitz.PDF_WIDGET_TYPE_RADIOBUTTON]:
                                print(f"  Selected: {widget.field_value}")
                        
                        if field_count == 0:
                            print("  No form fields found - this is a flattened PDF")
                    
                    # Also try to extract any annotations
                    print("\n\nANNOTATIONS:")
                    print("=" * 70)
                    
                    for page_num in range(doc.page_count):
                        page = doc[page_num]
                        annots = page.annots()
                        
                        for annot in annots:
                            print(f"\nPage {page_num + 1} Annotation:")
                            print(f"  Type: {annot.type}")
                            print(f"  Content: {annot.info}")
                    
                    doc.close()
                    os.unlink(pdf_path)
                    
                    return True
    
    return False

if __name__ == "__main__":
    check_pdf_form_fields()