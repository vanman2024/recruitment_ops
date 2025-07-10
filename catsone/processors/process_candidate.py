#!/usr/bin/env python3
"""
Main script to process candidate documents using Gemini LLM
Extracts only filled/checked information from questionnaires and resumes
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import traceback

# Add parent directory to path for pdf_to_images import
sys.path.append(str(Path(__file__).parent.parent))

from pdf_to_images import pdf_to_images
from config import *

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CandidateProcessor:
    def __init__(self):
        self.temp_dir = TEMP_DIR
        self.output_dir = OUTPUT_DIR
        self.prompts_dir = BASE_DIR / "prompts"
        
    def load_prompt(self, prompt_name):
        """Load a prompt template from file"""
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
        
        with open(prompt_path, 'r') as f:
            return f.read()
    
    def convert_pdf_to_images(self, pdf_path):
        """Convert PDF to images for analysis"""
        logger.info(f"Converting PDF to images: {pdf_path}")
        
        # Create temp directory for this candidate
        candidate_name = Path(pdf_path).stem
        temp_folder = self.temp_dir / f"{candidate_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert PDF to images
        output_folder = pdf_to_images(pdf_path, temp_folder, IMAGE_DPI)
        
        if output_folder:
            image_files = sorted(output_folder.glob("*.jpg"))
            logger.info(f"Created {len(image_files)} images from PDF")
            return image_files
        else:
            raise Exception("Failed to convert PDF to images")
    
    def analyze_questionnaire(self, image_files):
        """Analyze questionnaire images using Gemini"""
        logger.info(f"Analyzing {len(image_files)} questionnaire images")
        
        # Load the questionnaire analyzer prompt
        prompt = self.load_prompt("questionnaire_analyzer")
        
        results = []
        
        # Process each image
        for idx, image_file in enumerate(image_files):
            logger.info(f"Processing page {idx + 1}/{len(image_files)}: {image_file.name}")
            
            # Call Gemini using MCP
            try:
                # Using the Gemini MCP tool to analyze the image
                import subprocess
                import json
                
                # Construct the MCP command
                gemini_command = [
                    "python", "-m", "mcp",
                    "call",
                    "mcp__gemini__analyze_image",
                    json.dumps({
                        "image_path": str(image_file),
                        "prompt": prompt,
                        "model": GEMINI_MODEL
                    })
                ]
                
                # Execute the command
                result = subprocess.run(
                    gemini_command,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).parent.parent)
                )
                
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    results.append({
                        "page": idx + 1,
                        "content": response.get("content", "")
                    })
                else:
                    logger.error(f"Gemini error on page {idx + 1}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error processing page {idx + 1}: {str(e)}")
                
        return results
    
    def analyze_resume(self, pdf_path):
        """Analyze resume PDF"""
        logger.info(f"Analyzing resume: {pdf_path}")
        
        # Convert resume to images
        image_files = self.convert_pdf_to_images(pdf_path)
        
        # Load resume analyzer prompt
        resume_prompt = """
        Analyze this resume and extract the following information:
        1. Candidate name and contact information
        2. Relevant heavy equipment experience (years, types, brands)
        3. Certifications and licenses
        4. Key skills related to heavy equipment operation
        5. Work history with relevant positions
        
        Return the information in a clean, structured JSON format.
        """
        
        results = []
        for image_file in image_files:
            try:
                # Similar Gemini call as questionnaire
                import subprocess
                
                gemini_command = [
                    "python", "-m", "mcp",
                    "call", 
                    "mcp__gemini__analyze_image",
                    json.dumps({
                        "image_path": str(image_file),
                        "prompt": resume_prompt,
                        "model": GEMINI_MODEL
                    })
                ]
                
                result = subprocess.run(
                    gemini_command,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).parent.parent)
                )
                
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    results.append(response.get("content", ""))
                    
            except Exception as e:
                logger.error(f"Error analyzing resume: {str(e)}")
                
        return "\n".join(results)
    
    def merge_candidate_data(self, resume_data, questionnaire_data):
        """Merge resume and questionnaire data into final summary"""
        logger.info("Merging candidate data")
        
        # Parse questionnaire results
        filled_items = {}
        for page_result in questionnaire_data:
            try:
                content = page_result.get("content", "")
                if content and content.strip():
                    # Try to parse as JSON
                    if content.startswith("{"):
                        page_data = json.loads(content)
                        # Merge with existing data
                        for key, value in page_data.items():
                            if key not in filled_items:
                                filled_items[key] = value
                            elif isinstance(value, dict) and isinstance(filled_items[key], dict):
                                filled_items[key].update(value)
                            elif isinstance(value, list) and isinstance(filled_items[key], list):
                                filled_items[key].extend(value)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse page content as JSON")
        
        # Combine with resume data
        summary = {
            "timestamp": datetime.now().isoformat(),
            "resume_summary": resume_data,
            "questionnaire_data": filled_items
        }
        
        return summary
    
    def format_email_summary(self, candidate_data):
        """Format the data into a clean email summary"""
        logger.info("Formatting email summary")
        
        email_text = []
        email_text.append("CANDIDATE SUMMARY")
        email_text.append("=" * 50)
        email_text.append("")
        
        # Resume section
        if candidate_data.get("resume_summary"):
            email_text.append("RESUME HIGHLIGHTS:")
            email_text.append(candidate_data["resume_summary"])
            email_text.append("")
        
        # Questionnaire section
        if candidate_data.get("questionnaire_data"):
            email_text.append("QUESTIONNAIRE RESPONSES:")
            email_text.append("-" * 30)
            
            q_data = candidate_data["questionnaire_data"]
            
            # Equipment experience
            if "equipment_experience" in q_data:
                email_text.append("\nEQUIPMENT EXPERIENCE:")
                exp = q_data["equipment_experience"]
                if "brands" in exp:
                    email_text.append(f"  Brands: {', '.join(exp['brands'])}")
                if "years" in exp:
                    email_text.append(f"  Years: {exp['years']}")
            
            # Shovel experience
            if "shovel_experience" in q_data:
                email_text.append("\nSHOVEL EXPERIENCE:")
                exp = q_data["shovel_experience"]
                if "types" in exp:
                    email_text.append(f"  Types: {', '.join(exp['types'])}")
                if "brands" in exp:
                    email_text.append(f"  Brands: {', '.join(exp['brands'])}")
                if "years" in exp:
                    email_text.append(f"  Years: {exp['years']}")
            
            # Certifications
            if "certifications" in q_data:
                email_text.append("\nCERTIFICATIONS:")
                for cert, value in q_data["certifications"].items():
                    if value:
                        email_text.append(f"  ✓ {cert.replace('_', ' ').title()}")
        
        email_text.append("")
        email_text.append("=" * 50)
        
        return "\n".join(email_text)
    
    def process_candidate(self, resume_path, questionnaire_path, candidate_name=None):
        """Main processing function"""
        try:
            if not candidate_name:
                candidate_name = Path(resume_path).stem
            
            logger.info(f"Processing candidate: {candidate_name}")
            
            # Process resume
            resume_data = ""
            if resume_path and Path(resume_path).exists():
                resume_data = self.analyze_resume(resume_path)
            
            # Process questionnaire
            questionnaire_data = []
            if questionnaire_path and Path(questionnaire_path).exists():
                image_files = self.convert_pdf_to_images(questionnaire_path)
                questionnaire_data = self.analyze_questionnaire(image_files)
            
            # Merge data
            candidate_data = self.merge_candidate_data(resume_data, questionnaire_data)
            
            # Format email summary
            email_summary = self.format_email_summary(candidate_data)
            
            # Save outputs
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save JSON data
            json_path = self.output_dir / f"{candidate_name}_{timestamp}_data.json"
            with open(json_path, 'w') as f:
                json.dump(candidate_data, f, indent=2)
            logger.info(f"Saved candidate data to: {json_path}")
            
            # Save email summary
            email_path = self.output_dir / f"{candidate_name}_{timestamp}_email.txt"
            with open(email_path, 'w') as f:
                f.write(email_summary)
            logger.info(f"Saved email summary to: {email_path}")
            
            return {
                "success": True,
                "json_path": str(json_path),
                "email_path": str(email_path),
                "email_summary": email_summary
            }
            
        except Exception as e:
            logger.error(f"Error processing candidate: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Command line interface"""
    if len(sys.argv) < 3:
        print("Usage: python process_candidate.py <resume_pdf> <questionnaire_pdf> [candidate_name]")
        print("\nExample:")
        print("  python process_candidate.py resume.pdf questionnaire.pdf 'John Doe'")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    questionnaire_path = sys.argv[2]
    candidate_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Process the candidate
    processor = CandidateProcessor()
    result = processor.process_candidate(resume_path, questionnaire_path, candidate_name)
    
    if result["success"]:
        print("\nProcessing complete!")
        print(f"JSON data saved to: {result['json_path']}")
        print(f"Email summary saved to: {result['email_path']}")
        print("\n" + "="*50)
        print("EMAIL SUMMARY:")
        print("="*50)
        print(result["email_summary"])
    else:
        print(f"\nProcessing failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()