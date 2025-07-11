#!/usr/bin/env python3
"""
View the local PDF from Downloads
"""

import fitz  # PyMuPDF
import os

def convert_pdf_to_images():
    """Convert local PDF to images for viewing"""
    
    pdf_path = "/mnt/c/Users/angel/Downloads/Recruiting - Dayforce (1).pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF not found at: {pdf_path}")
        return
    
    print(f"Opening PDF: {pdf_path}")
    
    # Open PDF
    doc = fitz.open(pdf_path)
    
    print(f"PDF has {doc.page_count} pages")
    
    # Convert each page to image
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # Higher resolution for better quality
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        
        # Save as PNG
        output_path = f"/home/gotime2022/recruitment_ops/local_pdf_page_{page_num + 1}.png"
        pix.save(output_path)
        
        print(f"Saved page {page_num + 1} to: {output_path}")
    
    doc.close()
    
    print("\nAll pages converted successfully!")
    print("\nLet's look at page 4 (where Red Seal question should be):")

if __name__ == "__main__":
    convert_pdf_to_images()